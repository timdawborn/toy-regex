import regex


TESTS = ['ae', 'adddde', 'abce', 'abcdddddbcddde', 'chicken', 'abde', 'a', '', 'abcd']

r = regex.compile(r'a(bc|d*)*e')
for test in TESTS:
    print(r.accepts(test))
