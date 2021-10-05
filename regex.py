from fsa import DFAState, nfa_to_dfa

from regex_parser import Parser


class CompiledRegex:
    def __init__(self, string: str, dfa: DFAState):
        self.string = string
        self.dfa = dfa

    def accepts(self, string: str) -> bool:
        return self.dfa.accepts(string)


class NameGenerator:
    upto: int

    def __init__(self, start: int = 0):
        self.upto = start

    def __call__(self) -> str:
        s = f'q{self.upto}'
        self.upto += 1
        return s


def compile(string: str):
    # Parse the regex string into a tree of Node objects.
    node = Parser(string).parse()

    # Convert the tree of Node objects into a graph of NFAState objects.
    name_generator = NameGenerator()
    nfa_start, nfa_end = node.build_nfa(name_generator)
    nfa_end.set_accepting()

    # Convert the NFA to a DFA.
    dfa_start = nfa_to_dfa(nfa_start)

    # Return the DFA wrapped in a helper class.
    return CompiledRegex(string, dfa_start)
