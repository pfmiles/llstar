import util
# define data structures used in ll(*) analysis

epsilon = object() # represents epsilon transition edge

MAX_REC_DEPTH = 10 # maximum recursion depth when closuring

class terminal(object):
    def __init__(self, content):
        self.content = content
    def _repr__(self):
        return "terminal(%r)" % (self.content)
    def __str__(self):
        return self.content
    def __eq__(self, other):
        if not isinstance(other, terminal):
            return False
        return self.content == other.content
    def __hash__(self):
        return hash(self.content)
    
class non_terminal(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "non_terminal(%r)" % self.name
    def __str__(self):
        return self.name
    def __eq__(self, other):
        if not isinstance(other, non_terminal):
            return False
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)

# ATN state, not a 'configuration'
class atn_state(object):
    def __init__(self, name, final=False):
        self.name = name # state name, int or str
        self.transitions = []
        self.final = final
    def add_transition(self, edge, another_state):
        # edge could be either epsilon, terminal, non-terminal
        if not isinstance(edge, terminal) and not isinstance(edge, non_terminal) and epsilon != edge: 
            raise Exception("ATN transition edge added could only be epsilon, terminal or non-terminals.")
        if not isinstance(another_state, atn_state):
            raise Exception("Destination state should be another ATN state")
        self.transitions.append((edge, another_state))
    def __repr__(self):
        return "atn_state(%r)" % self.name
    def __str__(self):
        return self.name
    def __eq__(self, other):
        if not isinstance(other, atn_state):
            return False
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)
    def is_stop_state(self):
        return self.final
    def transit(self, e):
        ret = set()
        for (edge, s) in self.transitions:
            if e == edge:
                ret.add(s)
        return ret
    
class call_stack(object):
    def __init__(self):
        self.stack = []
    def __eq__(self, other):
        if not isinstance(other, call_stack):
            return False
        if self.stack == other.stack:
            return True
        elif self.is_empty() or other.is_empty():
            return True
        else:
            return util.is_suffix(self.stack, other.stack) if len(self.stack) > len(other.stack) else util.is_suffix(other.stack, self.stack)
    def is_empty(self):
        return len(self.stack) == 0
    def __hash__(self):
        return 0
    def __str__(self):
        return str(self.stack)
    def push(self, a_state):
        self.stack.append(a_state)
    def copy_and_pop(self): # duplicate this stack and pop
        stack1 = call_stack()
        stack1.stack = list(self.stack)
        return (stack1.stack.pop(), stack1)
    def get_rec_depth(self, a_state):
        return self.stack.count(a_state)
    
class atn_config(object):
    def __init__(self, a_state, alt, stack=call_stack(), pred=None):
        self.a_state = a_state
        self.alt = alt
        self.stack = stack
        if pred != None and not hasattr(pred, 'pred'):
            raise Exception("Predicates must have a method named 'pred' which returns true/false.")
        self.pred = pred
        self.was_resolved = False
    def __str__(self):
        return "(%s, %s, %s, %s)" % (self.a_state, self.alt, self.stack, self.pred)
    def __eq__(self, other):
        if not isinstance(other, atn_config):
            return False
        return self.a_state == other.a_state and self.alt == other.alt and self.stack == other.stack and self.pred == other.pred
    def __hash__(self):
        return hash(`hash(self.a_state) + hash(self.alt) + hash(self.stack) + hash(self.pred)`)

class dfa_state(object):
    def __init__(self, alt= -1):
        self.confs = set() # containing confs
        self.overflowed = False # whether recursion overflowed when closuring
        self.busy = set() # conf contained in this dfa_state which is closured
        self.recursive_alts = set()
        self.alt = alt # predicting alt of this dfa, -1 when not determined, only final dfa states has valid(greater than -1) alt number
    def __eq__(self, other):
        if not isinstance(other, dfa_state):
            return False
        return self.confs == other.confs
    def __hash__(self):
        return hash(`reduce(lambda x, y:x + y, [hash(x) for x in self.confs])`)
    def add_conf(self, conf):
        self.confs.add(conf)
    def __str__(self):
        return "{%s}" % ", ".join([str(x) for x in self.confs])
    # fetch all confs which has a pred and predicting alternative 'alt'
    def get_confs_with_preds_of_alt(self, alt):
        ret = set()
        for c in self.confs:
            if c.pred != None and alt == c.alt:
                ret.add(c)
        return ret
    def remove_conf(self, conf):
        self.confs.remove(conf)
    def add_all_confs(self, confs):
        self.confs.update(confs)
    def is_final(self):
        return self.alt > -1
    def get_all_predicting_alts(self):
        if self.is_final():
            return {self.alt}
        else:
            ret = set()
            for c in self.confs:
                ret.add(c.alt)
            return ret
    def get_all_terminal_edges(self):
        ret = set()
        for c in self.confs:
            a_state = c.a_state
            for (e, _) in a_state.transitions:
                if isinstance(e, terminal):
                    ret.add(e)
        return ret
    def move(self, t):
        ret = set()
        for (p, i, y, pi) in self.confs:
            dests = p.transit(t)
            if len(dests) == 0:
                continue
            else:
                for d in dests:
                    ret.add((d, i, y, pi))
        return ret
    
# dummy pred used in experiments
class dummy_pred(object):
    def __init__(self, result): # result should be True or False
        self.result = result
    def pred(self):
        return self.result
    def __str__(self):
        return `self.result`

# the whole atn network
class atn(object):
    def __init__(self):
        self.states = set() # all atn_states
        self.states_rule_mapping = dict() # atn_states to corresponding non-terminal mapping
        self.n_term_start_state_mapping = dict() # terminal to corresponding start atn_state mapping
        
    def get_rule_of_state(self, a_state):
        return self.states_rule_mapping[a_state]
    def get_all_destinations_of(self, edge):
        ret = set()
        for s in self.states:
            for (e, s) in s.transitions:
                if e == edge:
                    ret.add(s)
        return ret
    def get_start_state(self, n_term):
        return self.n_term_start_state_mapping[n_term]
    
# a dfa for a specific rule
class dfa(object):
    def __init__(self):
        self.states = set()
        self.final_referers = dict()
    def add_state(self, d_state):
        self.states.add(d_state)
    def contain_state(self, d_state):
        return d_state in self.states
    def add_final_state_and_referer(self, alt, d_state):
        self.states.add(d_state)
        self.final_referers[alt] = dfa_final_referer(d_state)
    def overide_final_state(self, alt, d_state):
        self.states.remove(self.final_referers[alt].state) # delete old final state
        self.final_referers[alt].state = d_state # final handler point to the new final state
    
# retargetable dfa final state
class dfa_final_referer(object):
    def __init__(self, d_state):
        self.state = d_state
