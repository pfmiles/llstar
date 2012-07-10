from atn_creation import rule
from algos import create_dfa, globals_holder
from datastructure import atn

# test for empty alternative production in grammar rule
# A ::= a
#     |
r = rule('A').ele('a')
r.alt()
print r

globals_holder.a_net = atn()
r.to_atn(globals_holder.a_net)

d_a = create_dfa(globals_holder.a_net.get_start_state(r.get_n_term_this_rule()))

globals_holder.a_net.to_png("A")

d_a.to_png("A_dfa")