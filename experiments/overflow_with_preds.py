from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# lookahead go over a recursive rule(overflowed, resolved by choosing earlier defined alternative)
# S ::= A $
# A ::= {pred1}? B a
#     | {pred2}? b* c
# B ::= b+ B

ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

rb = rule('B')
ra.ele('B').ele('a').pred('pred1')
ra.alt().ks('b').ele('c').pred('pred2')
print ra

rb.kc('b').ele('B')
print rb

globals_holder.a_net = atn()
rs.merge_to_atn(globals_holder.a_net)
ra.merge_to_atn(globals_holder.a_net)
rb.merge_to_atn(globals_holder.a_net)

d_a = create_dfa(ra.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png('A')

d_a.to_png('A_dfa')
