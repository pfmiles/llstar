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
    
# alg.10 in paper
def resolve(d_state):
    # find conflict alts
    conflicts = set()
    conflict_k = None
    ss_alt = dict() # (state, stack) -> [alts]
    ss_c = dict()
    for c in d_state.confs:
        k = (c.a_state, c.stack)
        if not k in ss_alt:
            ss_alt[k] = set()
        if not k in ss_c:
            ss_c[k] = []
        ss_alt[k].add(c.alt)
        ss_c[k].append(c)
    for k, v in ss_alt.iteritems():
        if len(v) > 1:
            conflicts = v
            conflict_k = k
            break # only one conflict set may exist
    # if no conflicts or overflow, return
    if len(conflicts) == 0 and not d_state.overflowed:
        return
    # if conflicts resolved by preds, return
    if resolve_with_preds(d_state, conflicts):
        return
    else:
        # resolve conflicts by alt defining order
        min_alt = min(conflicts)
        ccs = ss_c[conflict_k]
        for c in ccs:
            if c.alt != min_alt:
                d_state.remove_conf(c)
    if d_state.overflowed:
        print "%s overflowed, resolved by selecting the first predicting alternative." % d_state
    else:
        print "%s has conflict predicting alternatives: %s, resolved by selecting the first alt." % (d_state, conflicts)
    
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
                    raise Exception("Likely non-LL regular, recursive alts: " + `d_state.recursive_alts` + ", rule: " + `globals_holder.a_net.get_rule_of_state(p)`)
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
    work.append(D0)
    ret.add_state(D0)
    while len(work) != 0:
        d_state = work.pop()
        for a in d_state.get_all_terminal_edges():
            d_state_new = dfa_state()
            for conf in d_state.move(a): # move and closure
                d_state_new.add_all_confs(closure(d_state, conf))
            if not ret.contain_state(d_state_new): # resolve and add to nfa network
                resolve(d_state_new)
                predicting_alts = d_state_new.get_all_predicting_alts()
                if len(predicting_alts) == 1:
                    d_state_new.alt = iter(predicting_alts).next()
                    ret.override_final_state(d_state_new.alt, d_state_new)
                else:
                    work.append(d_state_new)
                ret.add_state(d_state_new)
            d_state.add_transition(a, d_state_new)
        for c in [c for c in d_state.confs if c.was_resolved]:
            d_state.add_transition(c.pred, ret.final_states[c.alt])
    return ret
