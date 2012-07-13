from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# S ::= A $
# A ::= b
#     | b
#     | b
#     | b c

ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

ra.ele('b')
ra.alt().ele('b')
ra.alt().ele('b')
ra.alt().ele('b').ele('c')
print ra

globals_holder.a_net = atn()

rs.merge_to_atn(globals_holder.a_net)
ra.merge_to_atn(globals_holder.a_net)

d_a = create_dfa(ra.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png('A')
d_a.to_png('A_dfa')
