# some scripts to create atn network
from datastructure import terminal, atn, dummy_pred, atn_state, epsilon, non_terminal, seq_gen

# NOTE: this implementation does not support nested kleene closure structure, since this is an experiment, it needn't :)

class rule(object): # grammar rule creator
    name_rule_mapping = dict()
    seq = seq_gen() # atn state number generator, global to all grammar rules
    @staticmethod
    def reset(): # reset the rule creator
        rule.name_rule_mapping.clear()
        rule.seq.reset()
    def __init__(self, name):
        self.name = name
        self.alts = [[]]
        self.preds = dict()
        rule.name_rule_mapping[name] = non_terminal(self.name)
    def ele(self, name): # name of terminals are lower-cased, non-terminals are upper-cased
        last_alt = self.alts[-1]
        if name.islower():
            last_alt.append(terminal(name))
        else:
            if name not in rule.name_rule_mapping:
                raise Exception("Undefined non-terminal: " + name)
            last_alt.append(rule.name_rule_mapping[name])
        return self
    def ks(self, *elements):
        return self.__kleene(kleene_star, *elements)
    def __kleene(self, constructor, *elements):
        eles = []
        for e in elements:
            if e.islower():
                eles.append(terminal(e))
            else:
                if e not in self.name_rule_mapping:
                    raise Exception("Undefined non-terminal: " + e)
                eles.append(rule.name_rule_mapping[e])
        ks = constructor(eles)
        last_alt = self.alts[-1]
        last_alt.append(ks)
        return self
    def kc(self, *elements):
        return self.__kleene(kleene_cross, *elements)
    def opt(self, *elements):
        return self.__kleene(optional, *elements)
    def alt(self):
        self.alts.append([])
        return self
    def pred(self, tf):
        alt_index = len(self.alts) - 1
        self.preds[alt_index] = dummy_pred(tf)
        return self
    def __str__(self):
        ret = self.name + " ::= "
        matches = []
        for i, alt in enumerate(self.alts):
            match_str = ' '.join([str(e) for e in alt])
            if i in self.preds:
                match_str = match_str + " if " + str(self.preds[i])
            matches.append(match_str)
        for i, match_str in enumerate(matches):
            if i == 0:
                ret = ret + match_str + '\n'
            else:
                ret = ret + '    | ' + match_str + '\n'
        return ret
    def __gen_atn_transitions(self, start_state, ts, end_state, a_net):
        cur_state = start_state
        for t in ts[0:-1]:
            if not isinstance(t, terminal) and not isinstance(t, non_terminal):
                raise Exception("Illegal transition edge: " + str(t))
            pn = self.__new_atn_state(str(rule.seq.next_num()), a_net)
            cur_state.add_transition(t, pn)
            cur_state = pn
        cur_state.add_transition(ts[-1], end_state)
    def __new_atn_state(self, name_suf, a_net, is_final=False): # create new atn_state
        ret = atn_state("p" + str(name_suf), is_final)
        a_net.states.add(ret)
        a_net.states_rule_mapping[ret] = self.get_n_term_this_rule()
        return ret
    def get_n_term_this_rule(self): # get the non-terminal representing this rule
        return rule.name_rule_mapping[self.name]
    def to_atn(self, a_net=atn()):
        ret = a_net
        pa = self.__new_atn_state(self.name, ret)# start state
        ret.n_term_start_state_mapping[self.get_n_term_this_rule()] = pa
        pa1 = self.__new_atn_state(self.name + "_end", ret, True) # end state
        for i, alt in enumerate(self.alts):
            pai = self.__new_atn_state(self.name + "_" + str(i), ret) # alt start state
            pa.add_transition(epsilon, pai) # start state epsilon transition to alt start state
            if len(alt) != 0:
                p0 = self.__new_atn_state(str(rule.seq.next_num()), ret) # element transitions start state
                if i in self.preds: # if pred for this alt exists
                    pai.add_transition(self.preds[i], p0)
                else:
                    pai.add_transition(epsilon, p0)
                # match seq transitions start
                cur_state = p0
                for ele in alt:
                    if isinstance(ele, terminal) or isinstance(ele, non_terminal):
                        next_state = self.__new_atn_state(str(rule.seq.next_num()), ret)
                        cur_state.add_transition(ele, next_state)
                        cur_state = next_state
                    elif isinstance(ele, kleene_star):
                        self.__gen_atn_transitions(cur_state, ele.eles, cur_state, ret) # gen transition circle
                    elif isinstance(ele, kleene_cross):
                        match_seq = ele.eles
                        next_state = self.__new_atn_state(str(rule.seq.next_num()), ret)
                        self.__gen_atn_transitions(cur_state, match_seq, next_state, ret)
                        self.__gen_atn_transitions(next_state, match_seq, next_state, ret)
                        cur_state = next_state
                    elif isinstance(ele, optional):
                        next_state = self.__new_atn_state(str(rule.seq.next_num()), ret)
                        cur_state.add_transition(epsilon, next_state)
                        self.__gen_atn_transitions(cur_state, ele.eles, next_state, ret)
                        cur_state = next_state
                    else:
                        raise Exception("Illegal transition edge: " + str(ele))
                #match seq transitions end
                cur_state.add_transition(epsilon, pa1) # epsilon transition to the end
            else:
                pai.add_transition(epsilon, pa1) # empty alt
        return ret
        
class kleene_star(object):
    def __init__(self, eles):
        self.eles = eles
    def __str__(self):
        return "(%s)*" % " ".join([str(e) for e in self.eles])

class kleene_cross(object):
    def __init__(self, eles):
        self.eles = eles
    def __str__(self):
        return "(%s)+" % " ".join([str(e) for e in self.eles])    
class optional(object):
    def __init__(self, eles):
        self.eles = eles
    def __str__(self):
        return "(%s)?" % " ".join([str(e) for e in self.eles])
