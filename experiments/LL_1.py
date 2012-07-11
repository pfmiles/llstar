from atn_creation import rule
from algos import create_dfa, globals_holder
from datastructure import atn

# simple LL(1) grammar
# S ::= A $
# A ::= a c*
#     | b c*
r = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs
r.ele('a').ks('c').pred(True)
r.alt().ele('b').ks('c')
print r

globals_holder.a_net = atn()
r.merge_to_atn(globals_holder.a_net)
rs.merge_to_atn(globals_holder.a_net)

d_s = create_dfa(rs.get_start_state(globals_holder.a_net))
d_net = create_dfa(r.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png('A')

d_s.to_png("S_dfa")
d_net.to_png('A_dfa')
