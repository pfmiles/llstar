from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# LL(2) grammar
# S ::= A $
# A ::= a b c+
#     | a d c?
r = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs
r.ele('a').ele('b').kc('c')
r.alt().ele('a').ele('d').opt('c')
print r
globals_holder.a_net = atn()
r.merge_to_atn(globals_holder.a_net)
rs.merge_to_atn(globals_holder.a_net)

d_s = create_dfa(rs.get_start_state(globals_holder.a_net))
d_net = create_dfa(r.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png('A')
d_net.to_png('A_dfa')
d_s.to_png("S_dfa")
