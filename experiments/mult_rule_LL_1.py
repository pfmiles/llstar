from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# multi-rule LL(1)
# S ::= A $
# A ::= a c+
#     | B
# B ::= b c+
#     | d c*
ra = rule('A')
rs = rule('S').ele('A').ele('eof')
rb = rule('B')

ra.ele('a').kc('c')
ra.alt().ele('B')

rb.ele('b').kc('c')
rb.alt().ele('d').ks('c')

globals_holder.a_net = atn()
ra.merge_to_atn(globals_holder.a_net)
globals_holder.a_net = rb.merge_to_atn(globals_holder.a_net)
rs.merge_to_atn(globals_holder.a_net)

s_dnet = create_dfa(rs.get_start_state(globals_holder.a_net))
a_dnet = create_dfa(ra.get_start_state(globals_holder.a_net))
b_dnet = create_dfa(rb.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png("A")
s_dnet.to_png("S_dfa")
a_dnet.to_png("A_dfa")
b_dnet.to_png("B_dfa")
