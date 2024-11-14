from typing import Generator, List, Tuple
from xyz.circuit import *

class QNode:
    def __init__(self, gate: QGate, dist: float = 0.0) -> None:
        self.name = str(gate)
        self.dist = dist
        self.gate: QGate = gate

class QNetwork:
    def __init__(self, num_qubits: int) -> None:
        self.__nodes: List[QNode] = []
        self.__edges: List[Tuple[int, int]] = []
        self.__node_fanins: List[List[int]] = []
        self.initialize(num_qubits)
        
    def initialize(self, num_qubits: int) -> None:
        self.__last_gate_on_qubit: List[int] = [-1] * num_qubits
        self.num_qubits = num_qubits
        for qubit in range(num_qubits):
            nodeIdx = self.add_node(QNode(f"q_{qubit}"))
            self.__last_gate_on_qubit[qubit] = nodeIdx
            
    def add_node(self, node: QNode) -> int:
        self.__nodes.append(node)
        return len(self.__nodes) - 1
    
    def add_gate(self, gate: QGate) -> int:
        nodeIdx = -1
        if issubclass(type(gate), BasicGate):
            nodeIdx = self.add_node(QNode(gate, gate.get_cnot_cost()))
            self.add_edge(self.__last_gate_on_qubit[gate.target_qubit.index], nodeIdx)
            self.__last_gate_on_qubit[gate.target_qubit.index] = nodeIdx
            if issubclass(type(gate), ControlledGate) or issubclass(type(gate), MultiControlledGate):
                for control_qubit in gate.get_control_qubits():
                    self.add_edge(self.__last_gate_on_qubit[control_qubit.index], nodeIdx)
                    self.__last_gate_on_qubit[gate.target_qubit.index] = nodeIdx
        return nodeIdx
        
    def add_edge(self, source: int, target: int) -> None:
        self.__edges.append((source, target))
        
    def to_dot(self) -> pydot.Dot:
        graph = pydot.Dot(graph_type="digraph")
        for idx, name in enumerate(self.__nodes):
            graph.add_node(pydot.Node(f"g_{idx}", label=self.levels[idx]))
        for source, target in self.__edges:
            graph.add_edge(pydot.Edge(f"g_{source}", f"g_{target}"))
        return graph
    
    def __dfs(self, node: int) -> None:
        for child in self.__node_fanins[node]:
            if not self.visited[child]:
                self.__dfs(child)
        self.__topological_order.append(node)
        self.visited[node] = True
    
    def traverse(self):
        self.__node_fanins = [[] for _ in range(len(self.__nodes))]
        self.__node_fanouts = [[] for _ in range(len(self.__nodes))]
        for u, v in self.__edges:
            self.__node_fanins[v].append(u)
            self.__node_fanouts[u].append(v)
        
        self.levels = [0.0] * len(self.__nodes)
        self.visited = [False] * len(self.__nodes)
        self.level = 0.0
        self.__topological_order = []
        for node in range(len(self.__nodes)):
            if len(self.__node_fanouts[node]) == 0:
                if not self.visited[node]:
                    self.__dfs(node)
        for node in self.__topological_order:
            for child in self.__node_fanins[node]:
                self.levels[node] = max(self.levels[child] + self.__nodes[node].dist, self.levels[node])


    def topological_order(self) -> Generator[QGate, None, None]:
        for node in self.__topological_order:
            yield self.__nodes[node].gate


def to_dag(circuit: QCircuit) -> QNetwork:
    q_network = QNetwork(circuit.get_num_qubits())
    for gate in circuit.get_gates():
        q_network.add_gate(gate)
    q_network.traverse()
    return q_network


def mapping(circuit: QCircuit) -> QCircuit:
    num_qubit: int = circuit.get_num_qubits()
    new_circuit = QCircuit(num_qubit)
    for i, gate in enumerate(to_dag(circuit).topological_order()):
        new_circuit.add_gate(gate)
    return new_circuit