import unittest

from fsa import DFAState


class TestDFAState(unittest.TestCase):
    def test_example(self):
        states = []
        for i in range(4):
            state = DFAState('q' + str(i))
            states.append(state)
        states[0].add_edge('a', states[0])
        states[0].add_edge('b', states[1])
        states[1].add_edge('a', states[3])
        states[1].add_edge('b', states[2])
        states[2].add_edge('a', states[3])
        states[2].add_edge('b', states[3])
        states[3].add_edge('a', states[3])
        states[3].add_edge('b', states[3])

        states[2].set_accepting()

        start = states[0]
        self.assertTrue(start.accepts('aaaabb'))
        self.assertFalse(start.accepts('chicken'))
