from algos import create_dfa, globals_holder
from atn_creation import rule

# LL(3) grammar
# A ::= a b c d?
#     | a b e d+
r = rule('A').ele('a').ele('b').ele('c').opt('d')
r.alt().ele('a').ele('b').ele('e').kc('d')

globals_holder.a_net = r.to_atn()
A = r.get_n_term_this_rule()
d_net = create_dfa(globals_holder.a_net.get_start_state(A))

globals_holder.a_net.to_png('A')
d_net.to_png('A_dfa')