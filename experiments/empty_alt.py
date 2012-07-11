from atn_creation import rule
from algos import create_dfa, globals_holder
from datastructure import atn

# test for empty alternative production in grammar rule
# S ::= A $
# A ::= a
#     |
r = rule('A')
rs = rule('S').ele('A').ele("eof")
print rs
r.ele('a')
r.alt()
print r

globals_holder.a_net = atn()
rs.merge_to_atn(globals_holder.a_net)
r.merge_to_atn(globals_holder.a_net)

d_s = create_dfa(rs.get_start_state(globals_holder.a_net))
d_a = create_dfa(r.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png("A")

d_s.to_png("S_dfa")
d_a.to_png("A_dfa")
