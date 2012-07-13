# define some basic algorithms of LL(*) analysis
from datastructure import call_stack, non_terminal, epsilon, MAX_REC_DEPTH, dfa_state, dfa, atn, atn_config

# holds any global vars required by those algorithms
class globals_holder(object):
    a_net = atn()
    def __init__(self):
        pass

# alg.11 in paper
def resolve_with_preds(d_state, conflicts):
    # alt -> atn_configs mapping
    pconfigs = dict()
    for i in conflicts:
        confs_with_preds = d_state.get_confs_with_preds_of_alt(i)
        if len(confs_with_preds) > 0:
            pconfigs[i] = confs_with_preds
    if len(pconfigs) < len(conflicts):
        return False
    for cs in pconfigs.values():
        for c in cs:
            c.was_resolved = True
    return True

def resolve_overflow(d_state):
    if not d_state.overflowed:
        return
    d_state.stop_transit = True # should stop compute when overflowed
    conflicts = d_state.get_all_predicting_alts() # overflowed, treat all predicting alts as conflicts
    if resolve_with_preds(d_state, conflicts):
        return
    min_alt = min(conflicts) # resolve_conflicts by removing all confs except the ones with min alt
    for c in list(d_state.confs):
        if c.alt != min_alt:
            d_state.remove_conf(c)
    print "%s overflowed, resolved by removing all alternative productions except the one defined first: %s" % (d_state, min_alt) 
    
# alg.10 in paper
def resolve_conflicts(d_state):
    # find conflict alts
    ss_alt = dict() # (state, stack) -> [alts]
    for c in d_state.confs:
        k = (c.a_state, c.stack)
        if not k in ss_alt:
            ss_alt[k] = set()
        ss_alt[k].add(c.alt)
    conflict_kvs = dict()
    for k, v in ss_alt.iteritems():
        if len(v) > 1:
            conflict_kvs[k] = v
    all_alts = d_state.get_all_predicting_alts()
    all_conflicts_contain_all_alts = True
    for v in conflict_kvs.itervalues():
        if v != all_alts:
            all_conflicts_contain_all_alts = False
            break
    # if no conflicts or any of the conflict configurations not contain all alts, return
    if len(conflict_kvs) == 0 or not all_conflicts_contain_all_alts:
        return
    
    d_state.stop_transit = True
    # if conflicts resolved by preds, return
    if resolve_with_preds(d_state, all_alts):
        return
    else:
        # resolve conflicts by alt defining order
        min_alt = min(all_alts)
        for c in list(d_state.confs):
            if c.alt != min_alt:
                d_state.remove_conf(c)
        print "%s has conflict predicting alternatives: %s, resolved by selecting the first alt." % (d_state, all_alts)
    
# alg.9 in paper
def closure(d_state, conf):
    # to prevent compute over and over again...
    if conf in d_state.busy:
        return set()
    else:
        d_state.busy.add(conf)
    ret = set()
    ret.add(conf)
    
    p, i, y, pi = conf.a_state, conf.alt, conf.stack, conf.pred
    if p.is_stop_state():
        if y.is_empty():
            for p2 in globals_holder.a_net.get_all_destinations_of(globals_holder.a_net.get_rule_of_state(p)):
                ret.update(closure(d_state, atn_config(p2, i, call_stack(), pi)))
        else:
            p1, y1 = y.copy_and_pop()
            ret.update(closure(d_state, atn_config(p1, i, y1, pi)))
    for t, s in p.transitions:
        if isinstance(t, non_terminal): # is a non-terminal edge transition
            depth = y.get_rec_depth(s) # recursion depth of t at state s
            if depth == 1:
                d_state.recursive_alts.add(i)
                if len(d_state.recursive_alts) > 1:
                    raise Exception("Likely non-LL regular, recursive alts: " + str(d_state.recursive_alts) + ", rule: " + str(globals_holder.a_net.get_rule_of_state(p)))
            if depth >= MAX_REC_DEPTH:
                d_state.overflowed = True
                return ret
            # push destination state and doing closure with the starting state of t
            stk = y.copy()
            stk.push(s)
            ret.update(closure(d_state, atn_config(globals_holder.a_net.get_start_state(t), i, stk, pi)))
        elif hasattr(t, 'pred') or epsilon == t: # is predicate or epsilon transition
            ret.update(closure(d_state, atn_config(s, i, y, pi)))
    return ret

# alg.8 in paper
def create_dfa(a_start_state):
    ret = dfa()
    work = []
    D0 = dfa_state() # dfa start state for this rule
    for alt in range(len(a_start_state.transitions)): # init all final states, num of start state transitions is num of alts
        f_i = dfa_state(alt)
        ret.add_dummy_final_state(alt, f_i)
    for i, (_, pa_i) in enumerate(a_start_state.transitions):
        pi = None
        first_t = iter(pa_i.transitions).next()[0] # may have only one transition
        if first_t != epsilon and hasattr(first_t, 'pred'): # has predicate
            pi = first_t # pred
        D0.add_all_confs(closure(D0, atn_config(pa_i, i, call_stack(), pi)))
        D0.release_busy()
    work.append(D0)
    ret.add_state(D0)
    while len(work) != 0:
        d_state = work.pop()
        new_trans = [] # remember transitions newly added
        new_works_count = 0 # remember num of new works added
        new_states = set() # remember new states discovered
        for a in d_state.get_all_terminal_edges():
            d_state_new = dfa_state()
            for conf in d_state.move(a): # move and closure
                d_state_new.add_all_confs(closure(d_state, conf))
                d_state.release_busy()
                resolve_overflow(d_state) # d_state may be marked overflowed while closuring, so it must be resolved
                check_if_final_and_replace(d_state, ret)
                if d_state.stop_transit: break
            if d_state.stop_transit: break
            if not ret.contain_state(d_state_new): # resolve_conflicts and add to dfa network
                resolve_conflicts(d_state_new)
                if not check_if_final_and_replace(d_state_new, ret):
                    work.append(d_state_new)
                    new_works_count = new_works_count + 1
                ret.add_state(d_state_new)
                new_states.add(d_state_new)
                d_state.add_transition(a, d_state_new)
                new_trans.append((a, d_state_new))
            else:
                d_state.add_transition(a, ret.get_same_state(d_state_new)) # add the same state already in the dfa(not the newly created one)
                new_trans.append((a, ret.get_same_state(d_state_new)))
        if d_state.stop_transit: # remove newly added states, transitions and works if d_state.stop_transit
            for n_s in new_states:
                ret.states.remove(n_s)
            for t in new_trans:
                d_state.transitions.remove(t)
            for i in range(new_works_count):
                work.pop()
        for c in [c for c in d_state.confs if c.was_resolved]:
            d_state.add_transition(c.pred, ret.final_states[c.alt])
    return ret

def check_if_final_and_replace(d_state, d_net): # check if the specified d_state is final and if so, replace the old final state with the same alt number
    predicting_alts = d_state.get_all_predicting_alts()
    if len(predicting_alts) == 1: # is final
        d_state.alt = iter(predicting_alts).next()
        d_net.override_final_state(d_state.alt, d_state)
        d_state.stop_transit = True
        return True
    return False
    
