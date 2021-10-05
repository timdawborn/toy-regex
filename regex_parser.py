r"""
<re>        ::= <simple-re> ( "|" <re> )?
<simple-re> ::= <basic-re>+
<basic-re>  ::= <elem-re> "*"?
<elem-re>   ::= "(" <re> ")"
<elem-re>   ::= "\" ("*" | "(" | ")" | "|" | "\")  # Escaped character
<elem-re>   ::=    ¬("*" | "(" | ")" | "|" | "\")  # Regular character.
"""
from typing import List, Tuple

from fsa import EPSILON, NFAState

LBR = '('
RBR = ')'
STAR = '*'
PIPE = '|'
ESCAPE = '\\'
SPECIAL_CHARACTERS = frozenset({LBR, RBR, STAR, PIPE, ESCAPE})


class Node:
    def build_nfa(self, name_generator) -> Tuple[NFAState, NFAState]:
        raise NotImplementedError()


class TextNode(Node):
    token: str

    def __init__(self, token: str):
        self.token = token

    def build_nfa(self, name_generator) -> Tuple[NFAState, NFAState]:
        q0 = NFAState(name_generator())
        q1 = NFAState(name_generator())
        q0.add_edge(self.token, q1)
        return (q0, q1)


class StarNode(Node):
    child: Node

    def __init__(self, child: Node):
        self.child = child

    def build_nfa(self, name_generator) -> Tuple[NFAState, NFAState]:
        q_start = NFAState(name_generator())
        q_end = NFAState(name_generator())
        child_start, child_end = self.child.build_nfa(name_generator)
        q_start.add_edge(EPSILON, q_end)
        q_start.add_edge(EPSILON, child_start)
        child_end.add_edge(EPSILON, q_end)
        child_end.add_edge(EPSILON, child_start)
        return (q_start, q_end)


class UnionNode(Node):
    child1: Node
    child2: Node

    def __init__(self, child1: Node, child2: Node):
        self.child1 = child1
        self.child2 = child2

    def build_nfa(self, name_generator) -> Tuple[NFAState, NFAState]:
        q_start = NFAState(name_generator())
        q_end = NFAState(name_generator())
        child1_start, child1_end = self.child1.build_nfa(name_generator)
        child2_start, child2_end = self.child2.build_nfa(name_generator)
        q_start.add_edge(EPSILON, child1_start)
        q_start.add_edge(EPSILON, child2_start)
        child1_end.add_edge(EPSILON, q_end)
        child2_end.add_edge(EPSILON, q_end)
        return (q_start, q_end)


class ConcatNode(Node):
    children: List[Node]

    def __init__(self, *children: Node):
        self.children = list(children)

    def build_nfa(self, name_generator) -> Tuple[NFAState, NFAState]:
        q_start = NFAState(name_generator())
        q_end = NFAState(name_generator())
        prev_start = q_start
        for child in self.children:
            child_start, child_end = child.build_nfa(name_generator)
            prev_start.add_edge(EPSILON, child_start)
            prev_start = child_end
        child_end.add_edge(EPSILON, q_end)
        return (q_start, q_end)


class ParseError(Exception):
    pass


class Parser:
    tokens: str
    length: int
    upto: int

    def __init__(self, tokens: str):
        self.tokens = tokens
        self.length = len(self.tokens)
        self.upto = 0

    def end(self) -> bool:
        return self.upto == self.length

    def peek(self) -> str:
        return '' if self.end() else self.tokens[self.upto]

    def next(self):
        if not self.end():
            self.upto += 1

    def _parse_elem_re(self) -> Node:
        node: Node
        if self.peek() == LBR:  # <elem-re> ::= "(" <re> ")"
            self.next()
            node = self._parse_re()
            if self.peek() != RBR:
                raise ParseError('Closing bracket not found!')
            self.next()
        elif self.peek() == ESCAPE:
            self.next()
            character = self.peek()
            if character not in SPECIAL_CHARACTERS:
                raise ParseError(f'Found invalid character {character!r} after {ESCAPE}!')
            node = TextNode(character)
            self.next()
        elif self.peek() not in SPECIAL_CHARACTERS:
            node = TextNode(self.peek())
            self.next()
        else:
            raise ParseError(f'Invalid character found when parsing <elem-re>: {self.peek()!r}')
        return node

    def _parse_basic_re(self) -> Node:
        node = self._parse_elem_re()
        if self.peek() == STAR:
            node = StarNode(node)
            self.next()
        return node

    def _parse_simple_re(self) -> Node:
        nodes = []
        while not self.end():
            try:
                nodes.append(self._parse_basic_re())
            except ParseError:
                break
        if len(nodes) == 0:
            raise ParseError('Could not find any <basic-re>s while parsing <simple-re>.')
        return ConcatNode(*nodes)

    def _parse_re(self) -> Node:
        node = self._parse_simple_re()
        if self.peek() == PIPE:
            self.next()
            node2 = self._parse_re()
            node = UnionNode(node, node2)
        return node

    def parse(self) -> Node:
        node = self._parse_re()
        if not self.end():
            raise ParseError(f'Extra tokens found at end of string: {self.tokens[self.upto:]!r}')
        return node
