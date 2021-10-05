import unittest

import regex


class TestRegex(unittest.TestCase):
    r = regex.compile(r'a(bc|d*)*e')

    def test_positive_examples_from_lab_sheet(self):
        TESTS = ['ae', 'adddde', 'abce', 'abcdddddbcddde']
        for test in TESTS:
            self.assertTrue(self.r.accepts(test))

    def test_negative_examples_from_lab_sheet(self):
        TESTS = ['chicken', 'abde', 'a', '', 'abcd']
        for test in TESTS:
            self.assertFalse(self.r.accepts(test))
