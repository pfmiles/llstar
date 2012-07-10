from algos import create_dfa, globals_holder
from atn_creation import rule

# multi-rule LL(1)
# A ::= a c+
#     | B
# B ::= b c+
#     | d c*

rb = rule('B')

ra = rule('A').ele('a').kc('c')
ra.alt().ele('B')

rb.ele('b').kc('c')
rb.alt().ele('d').ks('c')

globals_holder.a_net = ra.to_atn()
globals_holder.a_net = rb.to_atn(globals_holder.a_net)

a_dnet = create_dfa(globals_holder.a_net.get_start_state(ra.get_n_term_this_rule()))
b_dnet = create_dfa(globals_holder.a_net.get_start_state(rb.get_n_term_this_rule()))

globals_holder.a_net.to_png("A")
a_dnet.to_png("A_dfa")
b_dnet.to_png("B_dfa")