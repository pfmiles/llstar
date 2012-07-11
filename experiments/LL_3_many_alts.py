from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# LL(3) grammar
# S ::= A $
# A ::= B a*
#     | C a+
#     | D a?
# B ::= a b c C
#     | a b c D
#     | d
# C ::= e f g D
#     | e f g h
# D ::= i j k l
#     | i j k m
rb = rule('B')
rc = rule('C')
rd = rule('D')
ra = rule('A')
rs = rule('S').ele('A').ele('eof')
print rs

ra.ele('B').ks('a')
ra.alt().ele('C').kc('a')
ra.alt().ele('D').opt('a')
print ra

rb.ele('a').ele('b').ele('c').ele('C')
rb.alt().ele('a').ele('b').ele('c').ele('D')
rb.alt().ele('d')
print rb

rc.ele('e').ele('f').ele('g').ele('D')
rc.alt().ele('e').ele('f').ele('g').ele('h')
print rc

rd.ele('i').ele('j').ele('k').ele('l')
rd.alt().ele('i').ele('j').ele('k').ele('m')
print rd

# gen atns
globals_holder.a_net = atn()
ra.merge_to_atn(globals_holder.a_net)
rb.merge_to_atn(globals_holder.a_net)
rc.merge_to_atn(globals_holder.a_net)
rd.merge_to_atn(globals_holder.a_net)
rs.merge_to_atn(globals_holder.a_net)

# gen dfas
d_a = create_dfa(ra.get_start_state(globals_holder.a_net))
d_b = create_dfa(rb.get_start_state(globals_holder.a_net))
d_c = create_dfa(rc.get_start_state(globals_holder.a_net))
d_d = create_dfa(rd.get_start_state(globals_holder.a_net))
d_s = create_dfa(rs.get_start_state(globals_holder.a_net))

globals_holder.a_net.to_png("A")

d_s.to_png("S_dfa")
d_a.to_png("A_dfa")
d_b.to_png("B_dfa")
d_c.to_png("C_dfa")
d_d.to_png("D_dfa")
