from atn_creation import rule
from algos import create_dfa, globals_holder

# simple LL(1) grammar
# A ::= a c*
#     | b c*
r = rule('A').ele('a').ks('c').pred(True)
r.alt().ele('b').ks('c')
globals_holder.a_net = r.to_atn()
A = r.get_n_term_this_rule()
d_net = create_dfa(globals_holder.a_net.get_start_state(A))

globals_holder.a_net.to_png('A')
d_net.to_png('A_dfa')
