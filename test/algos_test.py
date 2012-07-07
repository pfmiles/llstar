from datastructure import dfa_state, call_stack, dummy_pred, atn_config, atn_state
from algos import resolve
import unittest

class algos_test(unittest.TestCase):
    
    def test_resolve(self):
        d_state = dfa_state()

        a = atn_state("p0")
        c1 = atn_config(a, 0, call_stack(), dummy_pred(False))
        c2 = atn_config(a, 1, call_stack(), dummy_pred(False))
        c3 = atn_config(a, 2)
        d_state.add_conf(c1)
        d_state.add_conf(c2)
        d_state.add_conf(c3)
        
        d_state.overflowed = True
        resolve(d_state)
