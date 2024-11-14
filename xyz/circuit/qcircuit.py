from typing import List
import numpy as np
import pydot
from .qgate import *
from queue import Queue

class QCircuit:
    def __init__(
        self, num_qubits: int, map_gates: bool = False, qubits: list = None
    ) -> None:
        self.__gates: List[QGate] = []

        if qubits is not None:
            self.__qubits: List[QBit] = qubits[:]
        else:
            self.__qubits: List[QBit] = []
            self.init_qubits(num_qubits)

        # configures
        self.map_gates = map_gates

    def sub_circuit(self, supports: list) -> "QCircuit":
        qubits = [self.qubit_at(i) for i in supports]
        sub_circuit = QCircuit(len(qubits), map_gates=self.map_gates, qubits=qubits)
        return sub_circuit

    def get_num_qubits(self) -> int:
        return len(self.__qubits)

    def qubit_at(self, index: int) -> QBit:
        assert (
            index < self.get_num_qubits()
        ), f"index = {index} >= num_qubits = {self.get_num_qubits()}"
        return self.__qubits[index]

    def get_gates(self) -> List[QGate]:
        return self.__gates

    def add_gate(self, gate: QGate):
        self.add_gate_optimized(gate)

    def add_gates(self, gates: List[QGate]):
        self.add_gates_optimized(gates)

    def append_gate(self, gate: QGate):
        self.__gates.append(gate)

    def append_gates(self, gates: List[QGate]):
        self.__gates.extend(gates)

    def add_qubit(self, qubit: QBit):
        self.__qubits.append(qubit)

    def add_qubits(self, qubits: List[QBit]):
        self.__qubits.extend(qubits)

    def init_qubits(self, num_qubits: int):
        for i in range(num_qubits):
            self.add_qubit(QBit(i))

    def num_gates(self, gate_type: QGateType = None) -> int:
        if gate_type is None:
            return len(self.__gates)
        return len(
            [gate for gate in self.__gates if gate.get_qgate_type() == gate_type]
        )

    def get_cnot_cost(self) -> int:
        return sum([gate.get_cnot_cost() for gate in self.__gates])

    def __str__(self) -> str:
        qubit_index_list = [qubit.index for qubit in self.__qubits]
        qubit_index_list_str = ",".join([str(i) for i in qubit_index_list])
        return f"Circuit({qubit_index_list_str})"

    def add_gate_mapped(self, gate: QGate) -> None:
        if not self.map_gates:
            self.append_gate(gate)
            return

        match gate.qgate_type:
            case QGateType.MULTIPLEX_Y:
                gates = map_muxy(gate)
                self.append_gates(gates)

            case QGateType.MCRY:
                if len(gate.get_control_qubits()) >= 8:
                    gates = map_mcry_linear(gate)
                else:
                    gates = map_mcry(gate)

                # this may cause problem if the gates returned are still MCRYs
                self.add_gates(gates)

            case QGateType.MCMY:
                gates = map_mcmy(gate)

                self.add_gates(gates)

            case QGateType.CRY:
                gates = map_mcry(gate)
                self.append_gates(gates)

            case _:
                self.append_gate(gate)

    def add_gate_optimized(self, gate: QGate) -> None:
        match gate.get_qgate_type():
            case QGateType.CU:
                if gate.is_z_trivial():
                    reduced_gate = CRY(
                        gate.get_beta(),
                        gate.control_qubit,
                        gate.get_phase(),
                        gate.target_qubit,
                    )
                    self.add_gate_optimized(reduced_gate)
                elif gate.is_z_trivial_not():
                    reduced_gate = CRY(
                        -gate.get_beta(),
                        gate.control_qubit,
                        gate.get_phase(),
                        gate.target_qubit,
                    )
                    self.add_gate_optimized(reduced_gate)
                else:
                    self.add_gate_mapped(gate)

            case QGateType.RY:
                if gate.is_trivial():
                    return
                self.add_gate_mapped(gate)

            case QGateType.CRY:
                self.add_gate_mapped(gate)
            case QGateType.MCRY:
                if gate.has_zero_controls():
                    reduced_gate = RY(gate.theta, gate.target_qubit)
                    self.add_gate_optimized(reduced_gate)

                # other wise we can use the same method as CRY
                elif gate.has_one_control():
                    reduced_gate = CRY(
                        gate.theta,
                        gate.control_qubits[0],
                        gate.phases[0],
                        gate.target_qubit,
                    )
                    self.add_gate_optimized(reduced_gate)
                else:
                    self.add_gate_mapped(gate)
            case _:
                self.add_gate_mapped(gate)

    def add_gates_optimized(self, gates: List[QGate]) -> None:
        """
        Add a list of gates to the circuit, with optimization
        """
        for gate in gates:
            self.add_gate_optimized(gate)
            
            
class QNode:
    def __init__(self, name: str, dist: float = 0.0) -> None:
        self.name = name
        self.dist = dist

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
            if issubclass(type(gate), ControlledGate) or issubclass(type(gate), MultiControlledGate):
                nodeIdx = self.add_node(QNode(str(gate), gate.get_cnot_cost()))
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

def to_dag(circuit: QCircuit) -> QNetwork:
    q_network = QNetwork(circuit.get_num_qubits())
    for gate in circuit.get_gates():
        q_network.add_gate(gate)
    q_network.traverse()
    return q_network

def to_qasm(circuit: QCircuit) -> str:
    return circuit.to_qasm()


def to_figure(circuit_str: str) -> str:
    return (
        """
\\begin{figure}[h]
\\centering
\\mbox{
\\small
    \\Qcircuit @C=.4em @R=.3em {
"""
        + circuit_str
        + """
    }
}
\\caption{}
\\end{figure}
"""
    )


def theta_to_str(theta: float) -> str:
    theta_str = f"{theta:.2f}"
    if np.isclose(theta, np.pi):
        theta_str = "\\pi"
    elif np.isclose(theta, np.pi / 2):
        theta_str = "\\pi/2"
    elif np.isclose(theta, -np.pi / 2):
        theta_str = "-\\pi/2"
    elif np.isclose(theta, np.pi / 4):
        theta_str = "\\pi/4"
    elif np.isclose(theta, np.pi / 4 * 3):
        theta_str = "3\\pi/4"
    elif np.isclose(theta, -np.pi / 4):
        theta_str = "-\\pi/4"
    elif np.isclose(theta, -np.pi / 4 * 3):
        theta_str = "-3\\pi/4"
    elif np.isclose(theta, -np.pi / 8):
        theta_str = "-\\pi/8"
    elif np.isclose(theta, np.pi / 8):
        theta_str = "\\pi/8"
    return theta_str


def ry_box(theta: float) -> str:
    theta_str = theta_to_str(theta)
    return f"\\gate{{\\parbox{{0.6cm}}{{\\centering \\footnotesize $R_y$\\\\${theta_str}$}}}}"


def to_tikz(circuit: QCircuit) -> str:
    """
    to_tikz:
    convert the circuit to tikz code
    """
    tikz_str = ""

    n_gates = len(circuit.get_gates())
    n_qubits = circuit.get_num_qubits()

    PLACEHOLDER = "\\qw"
    qubit_str = [
        [PLACEHOLDER for i in range(n_gates + 2)]
        for _ in range(circuit.get_num_qubits())
    ]

    for i in range(n_qubits):
        qubit_str[i][0] = f"\\lstick{{q_{i}}}"

    for j, gate in enumerate(circuit.get_gates()):
        i = j + 1
        match gate.get_qgate_type():
            case QGateType.X:
                qubit_str[gate.target_qubit.index][i] = "\\gate{{X}}"
            case QGateType.RY:
                gate: RY
                qubit_str[gate.target_qubit.index][i] = ry_box(theta=gate.theta)
            case QGateType.CX:
                gate: CX
                control_type = "ctrl" if gate.phase else "ctrlo"
                control_dist = -gate.control_qubit.index + gate.target_qubit.index
                qubit_str[gate.control_qubit.index][
                    i
                ] = f"\\{control_type}{{{control_dist}}}"
                qubit_str[gate.target_qubit.index][i] = "\\targ"
            case QGateType.CRY:
                gate: CRY
                control_type = "ctrl" if gate.phase else "ctrlo"
                control_dist = -gate.control_qubit.index + gate.target_qubit.index
                qubit_str[gate.control_qubit.index][
                    i
                ] = f"\\{control_type}{{{control_dist}}}"
                qubit_str[gate.target_qubit.index][i] = ry_box(theta=gate.theta)
            case QGateType.MCRY:
                gate: MCRY
                for control_qubit, control_phase in zip(
                    gate.control_qubits, gate.phases
                ):
                    control_type = "ctrl" if control_phase else "ctrlo"
                    control_dist = -control_qubit.index + gate.target_qubit.index
                    qubit_str[control_qubit.index][
                        i
                    ] = f"\\{control_type}{{{control_dist}}}"
                qubit_str[gate.target_qubit.index][i] = ry_box(theta=gate.theta)
            case _:
                raise ValueError(f"Unsupported gate type {gate.get_qgate_type()}")

    tikz_str = " \\\\\n".join([" & ".join(qubit) for qubit in qubit_str])
    return to_figure(tikz_str)
