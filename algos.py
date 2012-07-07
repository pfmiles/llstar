# define some basic algorithms of LL(*) analysis
from datastructure import call_stack, non_terminal, epsilon, MAX_REC_DEPTH
from work_station import atn

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
            c.wasResolved = True
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
    # if conflicts resolved be preds, return
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
    closure = set()
    closure.add(conf)
    
    (p, i, y, pi) = (conf.a_state, conf.alt, conf.stack, conf.pred)
    if p.is_stop_state():
        if y.is_empty():
            for p2 in atn.get_all_destinations_of(atn.get_rule_of_state(p)):
                closure.update(closure(d_state, (p2, i, call_stack(), pi)))
        else:
            (p1, y1) = y.copy_and_pop()
            closure.update(closure(d_state, (p1, i, y1, pi)))
    for (t, s) in p.transitions:
        if isinstance(t, non_terminal): # is a non-terminal edge transition
            depth = y.get_rec_depth(s) # recursion depth of t at state s
            if depth == 1:
                d_state.recursive_alts.add(i)
                if len(d_state.recursive_alts) > 1:
                    raise Exception("Likely non-LL regular, recursive alts: " + `d_state.recursive_alts` + ", rule: " + `atn.get_rule_of_state(p)`)
            if depth >= MAX_REC_DEPTH:
                d_state.overflowed = True
                return closure
            # push destination state and doing closure with the starting state of t
            stk = y.copy()
            stk.push(s)
            closure.update(closure(d_state, (atn.get_start_state(t), i, stk, pi)))
        elif hasattr(t, 'pred') or epsilon == t: # is predicate or epsilon transition
            closure.update(closure(d_state, (s, i, y, pi)))
    return closure
