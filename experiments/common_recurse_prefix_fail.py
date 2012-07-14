from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# rule A's two alts both prefixed with recursive rule E, this should fail
# S ::= A eof
# A ::= E a
#     | E b
# E ::= c E d
#     | e

ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

re = rule('E')
ra.ele('E').ele('a')
ra.alt().ele('E').ele('b')
print ra

re.ele('c').ele('E').ele('d')
re.alt().ele('e')
print re

globals_holder.a_net = atn()

rs.merge_to_atn(globals_holder.a_net)
ra.merge_to_atn(globals_holder.a_net)
re.merge_to_atn(globals_holder.a_net)

d_a = create_dfa(ra.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png('A')

d_a.to_png('A_dfa')
