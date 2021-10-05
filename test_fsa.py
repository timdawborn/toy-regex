import unittest

from fsa import DFANode


class TestDFANode(unittest.TestCase):
    def test_example(self):
        nodes = []
        for i in range(4):
            node = DFANode('q' + str(i))
            nodes.append(node)
        nodes[0].add_edge('a', nodes[0])
        nodes[0].add_edge('b', nodes[1])
        nodes[1].add_edge('a', nodes[3])
        nodes[1].add_edge('b', nodes[2])
        nodes[2].add_edge('a', nodes[3])
        nodes[2].add_edge('b', nodes[3])
        nodes[3].add_edge('a', nodes[3])
        nodes[3].add_edge('b', nodes[3])

        nodes[2].set_accepting()

        start = nodes[0]
        self.assertTrue(start.accepts('aaaabb'))
        self.assertFalse(start.accepts('chicken'))
