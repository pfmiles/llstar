from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# lookahead analysis go over kleene nodes
# S ::= A $
# A ::= B* b
#     | C+ c
# B ::= a d
#     | e
# C ::= a d
#     | e

ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

rb = rule('B')
rc = rule('C')
ra.ks('B').ele('b')
ra.alt().kc('C').ele('c')
print ra

rb.ele('a').ele('d')
rb.alt().ele('e')
print rb

rc.ele('a').ele('d')
rc.alt().ele('e')
print rc

globals_holder.a_net = atn()

ra.merge_to_atn(globals_holder.a_net)
rs.merge_to_atn(globals_holder.a_net)
rb.merge_to_atn(globals_holder.a_net)
rc.merge_to_atn(globals_holder.a_net)

d_s = create_dfa(rs.get_start_state(globals_holder.a_net))
d_a = create_dfa(ra.get_start_state(globals_holder.a_net))
d_b = create_dfa(rb.get_start_state(globals_holder.a_net))
d_c = create_dfa(rc.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png("A")

d_s.to_png("S_dfa")
d_a.to_png("A_dfa")
d_b.to_png("B_dfa")
d_c.to_png("C_dfa")
