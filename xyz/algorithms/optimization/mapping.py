from typing import Generator, List, Tuple
from dataclasses import dataclass
from collections import deque
from xyz.circuit import *

class QNode:
    def __init__(self, gate: QGate, dist: float = 0.0) -> None:
        self.name = str(gate)
        self.dist = dist
        self.gate: QGate = gate if isinstance(gate, QGate) else None

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
            self.add_edge(self.__last_gate_on_qubit[gate.target_qubit.index], nodeIdx, label=f"q_{gate.target_qubit.index}")
            self.__last_gate_on_qubit[gate.target_qubit.index] = nodeIdx
            if issubclass(type(gate), ControlledGate) or issubclass(type(gate), MultiControlledGate):
                for control_qubit in gate.get_control_qubits():
                    self.add_edge(self.__last_gate_on_qubit[control_qubit.index], nodeIdx, label=f"q_{control_qubit.index}")
                    self.__last_gate_on_qubit[gate.target_qubit.index] = nodeIdx
        return nodeIdx
        
    def add_edge(self, source: int, target: int, label: str = "") -> None:
        self.__edges.append((source, target, label))
        
    def to_dot(self) -> pydot.Dot:
        graph = pydot.Dot(graph_type="digraph")
        for idx, node in enumerate(self.__nodes):
            if isinstance(node.gate, str):
                graph.add_node(pydot.Node(f"g_{idx}", label=node.gate))
            else:
                label = f"{node.gate.get_qgate_type()}"
                graph.add_node(pydot.Node(f"g_{idx}", label=label))
        for source, target, label in self.__edges:
            graph.add_edge(pydot.Edge(f"g_{source}", f"g_{target}", label=label))
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
        for u, v, _ in self.__edges:
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
class ChoiceType(Enum):
    SWAP = 0
    GATES = 2
    START = 3
    END = 4
    
@dataclass
class ChoiceNode:
    gate: QGate
    nodeType: ChoiceType # todo define enum if necessary
    children: List["ChoiceNode"]
    index: int = -1

class Mapper:

    def __init__(self) -> None:
        self.__rootNode = ChoiceNode([], ChoiceType.START, [])
        self.__currNode = self.__rootNode
        self.__nodeIdx = 0
        
    def getHead(self) -> ChoiceNode:
        return self.__currNode
    
    def createNode(self, gate: QGate, nodeType: ChoiceType, children: List[ChoiceNode]) -> ChoiceNode:
        node = ChoiceNode(gate, nodeType, children, self.__nodeIdx)
        self.__nodeIdx += 1
        return node
    
    def appendNode(self, node: ChoiceNode) -> None:
        self.__currNode.children.append(node)
        self.__currNode = node
        
    def appendGate(self, gate: QGate) -> None:
        node = self.createNode(gate, ChoiceType.GATES, [])
        self.appendNode(node)
        
    def createChoice(self, children: List[ChoiceNode]) -> ChoiceNode:
        node = self.createNode([], ChoiceType.CHOOSE, children)
        return node
    
    def dynamic_mapping(self, gate: QGate) -> ChoiceNode:
        match gate.get_qgate_type():
            case QGateType.MCRY:
                self.appendNode(ChoiceNode(gate, ChoiceType.GATES, []))
            case QGateType.CRY:
                # we have two commutable gates
                self.appendGate(CX(gate.control_qubit, gate.phase, gate.target_qubit))
                
                choice1 = ChoiceNode([
                    CX(gate.control_qubit, gate.phase, gate.target_qubit),
                    RY(-gate.theta / 2, gate.target_qubit), 
                    CX(gate.control_qubit, gate.phase, gate.target_qubit),
                ], ChoiceType.GATES, [])
                choice2 = ChoiceNode([
                    RY(gate.theta / 2, gate.target_qubit)
                ], ChoiceType.GATES, [])        
                return ChoiceNode([], ChoiceType.SWAP, [choice1, choice2])
            case _:
                return ChoiceNode([gate], ChoiceType.GATES, [])

def mapping(circuit: QCircuit) -> QCircuit:
    if circuit.map_gates == True:
        print(f"[WARNING] circuit has already been mapped, skipping mapping")
        return circuit
    num_qubit: int = circuit.get_num_qubits()
    
    new_circuit = QCircuit(num_qubit, map_gates=False)
    
    dag = to_dag(circuit)

    mapper = Mapper()
    
    for i, gate in enumerate(dag.topological_order()):
        # skip the qubit definition gates
        if gate is None:
            continue
        assert isinstance(gate, BasicGate), f"gate {gate} is not a basic gate"
        new_gate = gate
        # update the level of the qubits
        if issubclass(type(gate), ControlledGate) or issubclass(type(gate), MultiControlledGate):
            # print the control qubits and the levels
            print("-" * 80)
            print(f"gate {gate}")
            mapper.dynamic_mapping(gate)
        new_circuit.add_gate(new_gate)
    
    mapper.toGraph("mapping.dot")
    return new_circuit

def mapping_debug(circuit: QCircuit, reorder: bool = False) -> QCircuit:
    # just to test if this makes sense
    if circuit.map_gates == True:
        print(f"[WARNING] circuit has already been mapped, skipping mapping")
        return circuit

    # for each gate, we randomly permute the control qubits and run the decomposition
    num_qubit: int = circuit.get_num_qubits()
    new_circuit = QCircuit(num_qubit, map_gates=True)
    for i, gate in enumerate(circuit.get_gates()):
        if reorder == True and issubclass(type(gate), MultiControlledGate):
            control_qubits, phases = gate.get_control_qubits(), gate.get_phases()
            n = len(control_qubits)

            # sort the control qubits and phases according to new_circuit.get_level_on_qubit(control_qubits)
            ctrls = zip(control_qubits, phases)
            ctrls = sorted(ctrls, key=lambda x: new_circuit.get_level_on_qubit(x[0]))
            control_qubits, phases = zip(*ctrls)
            
            gate.set_control_qubits(control_qubits)
            gate.set_phases(phases)
            new_circuit.add_gate(gate)
        else:
            new_circuit.add_gate(gate)
            
    return new_circuit