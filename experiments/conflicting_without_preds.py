from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# grammar with conflicting alts, no predicates, select the first alternative by convention # TODO dangling DFA state
# S ::= A $
# A ::= B
#     | b
# B ::= b
#     | b

ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

rb = rule('B')
ra.ele('B')
ra.alt().ele('b')
print ra

rb.ele('b')
rb.alt().ele('b')
print rb

globals_holder.a_net = atn()

rs.merge_to_atn(globals_holder.a_net)
ra.merge_to_atn(globals_holder.a_net)
rb.merge_to_atn(globals_holder.a_net)

d_a = create_dfa(ra.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png('A')

d_a.to_png('A_dfa')
