from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# lookahead analysis go over kleene nodes
# S ::= A $
# A ::= a* b
#     | a+ c

ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

ra.ks('a').ele('b')
ra.alt().kc('a').ele('c')
print ra

globals_holder.a_net = atn()

ra.merge_to_atn(globals_holder.a_net)
rs.merge_to_atn(globals_holder.a_net)

d_s = create_dfa(rs.get_start_state(globals_holder.a_net))
d_a = create_dfa(ra.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png("A")

d_s.to_png("S_dfa")
d_a.to_png("A_dfa")