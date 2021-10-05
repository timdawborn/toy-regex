from typing import Dict, List, Optional, Set, Tuple

__all__ = ['EPSILON', 'DFANode', 'NFANode', 'nfa2dfa']

EPSILON: str = 'ε'


class DFANode:
    name: str
    edges: Dict[str, 'DFANode']
    is_accepting: bool

    def __init__(self, name: str):
        self.name = name
        self.edges = {}
        self.is_accepting = False

    def accepts(self, string: str) -> bool:
        if len(string) == 0:
            return self.is_accepting
        else:
            node = self.edges.get(string[0])
            if node is None:
                return False
            else:
                return node.accepts(string[1:])

    def add_edge(self, label: str, node: 'DFANode'):
        if len(label) != 1:
            raise ValueError(f'Label must be exactly one character long; got {label!r}')
        if label in self.edges:
            raise ValueError(f'Label {label} already exists as an edge!')
        self.edges[label] = node

    def follow_edge(self, label: str) -> Optional['DFANode']:
        return self.edges.get(label)

    def set_accepting(self):
        self.is_accepting = True

    def __str__(self):
        return f'DFANode({self.name!r})'


class NFANode:
    name: str
    edges: Dict[str, Set['NFANode']]
    is_accepting: bool

    def __init__(self, name: str):
        self.name = name
        self.edges = {}
        self.is_accepting = False

    def accepts(self, string: str) -> bool:
        if len(string) == 0:
            return self.is_accepting
        else:
            nodes = self.edges.get(string[0], set())
            for node in nodes:
                if node.accepts(string[1:]):
                    return True
            return False

    def add_edge(self, label: str, node: 'NFANode'):
        if len(label) != 1:
            raise ValueError(f'Label must be exactly one character long; got {label!r}')
        if label not in self.edges:
            self.edges[label] = set()
        self.edges[label].add(node)

    def get_edge_labels(self, *, include_epsilon: bool = True) -> Set[str]:
        labels = set(self.edges)
        if not include_epsilon:
            labels -= {EPSILON}
        return labels

    def follow_edge(self, label: str) -> Set['NFANode']:
        return self.edges.get(label, set())

    def set_accepting(self):
        self.is_accepting = True

    def __str__(self):
        return f'NFANode({self.name!r})'


def nfa2dfa(nfa_start: NFANode) -> DFANode:
    def move(nodes: Set[NFANode], label: str) -> Set[NFANode]:
        resulting_nodes: Set[NFANode] = set()
        for node in nodes:
            resulting_nodes.update(node.follow_edge(label))
        return resulting_nodes

    def epsilon_closure(nodes: Set[NFANode]) -> Set[NFANode]:
        return move(nodes, EPSILON)

    def make_dfa_name(nodes: Set[NFANode]) -> str:
        names = sorted(node.name for node in nodes)
        return '{' + ','.join(names) + '}'

    dfa_nodes_by_name: Dict[str, DFANode] = {}

    def get_or_create_dfa_node_for_nfa_nodes(nodes: Set[NFANode]) -> DFANode:
        name = make_dfa_name(nodes)
        dfa_node = dfa_nodes_by_name.get(name)
        if dfa_node is None:
            dfa_node = DFANode(name)
            dfa_nodes_by_name[name] = dfa_node
        return dfa_node

    nfa_start_nodes = epsilon_closure({nfa_start})
    dfa_start = get_or_create_dfa_node_for_nfa_nodes(nfa_start_nodes)

    todo: List[Tuple[DFANode, Set[NFANode]]] = [(dfa_start, nfa_start_nodes)]
    todo_names: Set[str] = {dfa_start.name}  # Set of processed DFANode names.

    while len(todo) != 0:
        # Grab the next item off the todo list.
        dfa_node, nfa_nodes = todo.pop(0)

        # Work out the set of edge labels.
        labels: Set[str] = set()
        for node in nfa_nodes:
            labels.update(node.get_edge_labels(include_epsilon=False))

        for label in labels:
            # Follow this edge label.
            new_nfa_nodes = epsilon_closure(move(nfa_nodes, label))
            if len(new_nfa_nodes) != 0:
                new_dfa_node = get_or_create_dfa_node_for_nfa_nodes(new_nfa_nodes)
                dfa_node.add_edge(label, new_dfa_node)

                if new_dfa_node.name not in todo_names:
                    todo.append((new_dfa_node, new_nfa_nodes))
                    todo_names.add(new_dfa_node.name)

    return dfa_start
