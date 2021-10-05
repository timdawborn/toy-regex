from fsa import DFAState, nfa2dfa

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
    node = Parser(string).parse()

    name_generator = NameGenerator()
    nfa_start, nfa_end = node.build_nfa(name_generator)
    nfa_end.set_accepting()

    dfa_start = nfa2dfa(nfa_start)
    return CompiledRegex(string, dfa_start)
