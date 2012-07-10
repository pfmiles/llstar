from algos import create_dfa, globals_holder
from atn_creation import rule
from datastructure import atn

# LL(3) grammar
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

ra = rule('A').ele('B').ks('a')
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
ra.to_atn(globals_holder.a_net)
rb.to_atn(globals_holder.a_net)
rc.to_atn(globals_holder.a_net)
rd.to_atn(globals_holder.a_net)

# gen dfas
d_a = create_dfa(globals_holder.a_net.get_start_state(ra.get_n_term_this_rule()))
d_b = create_dfa(globals_holder.a_net.get_start_state(rb.get_n_term_this_rule()))
d_c = create_dfa(globals_holder.a_net.get_start_state(rc.get_n_term_this_rule()))
d_d = create_dfa(globals_holder.a_net.get_start_state(rd.get_n_term_this_rule()))

globals_holder.a_net.to_png("A")

d_a.to_png("A_dfa")
d_b.to_png("B_dfa")
d_c.to_png("C_dfa")
d_d.to_png("D_dfa")
