from typing import Dict, List, Optional, Set, Tuple

__all__ = ['EPSILON', 'DFAState', 'NFAState', 'nfa_to_dfa']

EPSILON: str = 'ε'


class DFAState:
    name: str
    edges: Dict[str, 'DFAState']
    is_accepting: bool

    def __init__(self, name: str):
        self.name = name
        self.edges = {}
        self.is_accepting = False

    def accepts(self, string: str) -> bool:
        if len(string) == 0:
            return self.is_accepting
        else:
            state = self.edges.get(string[0])
            if state is None:
                return False
            else:
                return state.accepts(string[1:])

    def add_edge(self, label: str, state: 'DFAState'):
        if len(label) != 1:
            raise ValueError(f'Label must be exactly one character long; got {label!r}')
        if label in self.edges:
            raise ValueError(f'Label {label} already exists as an edge!')
        self.edges[label] = state

    def follow_edge(self, label: str) -> Optional['DFAState']:
        return self.edges.get(label)

    def set_accepting(self):
        self.is_accepting = True

    def __str__(self):
        return f'DFAState({self.name!r}, {self.edges}, {self.is_accepting})'

    def __repr__(self):
        return str(self)


class NFAState:
    name: str
    edges: Dict[str, Set['NFAState']]
    is_accepting: bool

    def __init__(self, name: str):
        self.name = name
        self.edges = {}
        self.is_accepting = False

    def accepts(self, string: str) -> bool:
        if len(string) == 0:
            return self.is_accepting
        else:
            states = self.edges.get(string[0], set())
            for state in states:
                if state.accepts(string[1:]):
                    return True
            return False

    def add_edge(self, label: str, state: 'NFAState'):
        if len(label) != 1:
            raise ValueError(f'Label must be exactly one character long; got {label!r}')
        if label not in self.edges:
            self.edges[label] = set()
        self.edges[label].add(state)

    def get_edge_labels(self, *, include_epsilon: bool = True) -> Set[str]:
        labels = set(self.edges)
        if not include_epsilon:
            labels -= {EPSILON}
        return labels

    def _get_epsilon_closure(self, seen: Set['NFAState']) -> Set['NFAState']:
        result = {self}
        targets = self.edges.get(EPSILON, set())
        for target in targets:
            if target not in seen:
                seen.add(target)
                result.update(target._get_epsilon_closure(seen))
        return result

    def get_epsilon_closure(self) -> Set['NFAState']:
        return self._get_epsilon_closure(set())

    def follow_edge(self, label: str) -> Set['NFAState']:
        return self.edges.get(label, set())

    def set_accepting(self):
        self.is_accepting = True

    def __str__(self):
        return f'NFAState({self.name!r}, {self.edges}, {self.is_accepting})'

    def __repr__(self):
        return str(self)


def nfa_to_dfa(nfa_start: NFAState) -> DFAState:
    def move(states: Set[NFAState], label: str) -> Set[NFAState]:
        resulting_states: Set[NFAState] = set()
        for state in states:
            resulting_states.update(state.follow_edge(label))
        return resulting_states

    def epsilon_closure(states: Set[NFAState]) -> Set[NFAState]:
        resulting_states: Set[NFAState] = set()
        for state in states:
            resulting_states.update(state.get_epsilon_closure())
        return resulting_states

    def make_dfa_name(states: Set[NFAState]) -> str:
        names = sorted(state.name for state in states)
        return '{' + ','.join(names) + '}'

    dfa_states_by_name: Dict[str, DFAState] = {}

    def get_or_create_dfa_state_for_nfa_states(states: Set[NFAState]) -> DFAState:
        name = make_dfa_name(states)
        dfa_state = dfa_states_by_name.get(name)
        if dfa_state is None:
            dfa_state = DFAState(name)
            if any(state.is_accepting for state in states):
                dfa_state.set_accepting()
            dfa_states_by_name[name] = dfa_state
        return dfa_state

    nfa_start_states = epsilon_closure({nfa_start})
    dfa_start = get_or_create_dfa_state_for_nfa_states(nfa_start_states)

    todo: List[Tuple[DFAState, Set[NFAState]]] = [(dfa_start, nfa_start_states)]
    seen: Set[DFAState] = {dfa_start}

    while len(todo) != 0:
        # Grab the next item off the todo list.
        dfa_state, nfa_states = todo.pop(0)

        # Work out the set of edge labels.
        labels: Set[str] = set()
        for state in nfa_states:
            labels.update(state.get_edge_labels(include_epsilon=False))

        for label in labels:
            # Follow this edge label.
            new_nfa_states = epsilon_closure(move(nfa_states, label))
            if len(new_nfa_states) != 0:
                new_dfa_state = get_or_create_dfa_state_for_nfa_states(new_nfa_states)
                dfa_state.add_edge(label, new_dfa_state)

                if new_dfa_state not in seen:
                    todo.append((new_dfa_state, new_nfa_states))
                    seen.add(new_dfa_state)

    return dfa_start
