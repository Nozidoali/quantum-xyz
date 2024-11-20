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
        self.__last_gate_target_on_qubit = [-1] * num_qubits
        self.__last_gate_time = [0] * num_qubits

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
        qubits = []
        if issubclass(type(gate), BasicGate):
            self.__last_gate_target_on_qubit[gate.target_qubit.index] = len(self.__gates) - 1
            if issubclass(type(gate), ControlledGate):
                qubits.append(gate.target_qubit)
                qubits.append(gate.control_qubit)
                gate_time = max(self.__last_gate_time[qubit.index] for qubit in qubits) 
                for qubit in qubits:
                    self.__last_gate_time[qubit.index] = gate_time + gate.get_cnot_cost()
            elif issubclass(type(gate), MultiControlledGate):
                qubits.append(gate.target_qubit)
                qubits.extend(gate.control_qubits)
                gate_time = max(self.__last_gate_time[qubit.index] for qubit in qubits) 
                for qubit in qubits:
                    self.__last_gate_time[qubit.index] = gate_time + gate.get_cnot_cost()
            
    def get_level(self) -> int:
        return max(self.__last_gate_time)
    
    def get_level_on_qubit(self, qubit: QBit) -> int:
        return self.__last_gate_time[qubit.index]
    
            
    def last_gate_on_qubit(self, qubit: QBit) -> QGate:
        idx = qubit.index if isinstance(qubit, QBit) else qubit
        return self.__last_gate_target_on_qubit[idx]
    
    def gate_at(self, index: int) -> QGate:
        return self.__gates[index]
    
    def remove_gate(self, index: int) -> None:
        self.__gates.pop(index)
        for i in range(index, len(self.__gates)):
            gate = self.__gates[i]
            if issubclass(type(gate), BasicGate):
                self.__last_gate_target_on_qubit[gate.target_qubit.index] = i

    def append_gates(self, gates: List[QGate]):
        for gate in gates:
            self.append_gate(gate)

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
    
    def trim(self, start, end) -> 'QCircuit':
        qubits = [qubit for qubit in self.__qubits]
        gates = [gate for gate in self.__gates[start:end]]
        new_circuit = QCircuit(len(qubits), map_gates=self.map_gates, qubits=qubits)
        new_circuit.append_gates(gates)
        return new_circuit
    
def reverse_circuit(circuit: QCircuit) -> QCircuit:
    new_circuit = QCircuit(circuit.get_num_qubits(), map_gates=circuit.map_gates)
    for gate in reversed(circuit.get_gates()):
        new_circuit.add_gate(gate)
    return new_circuit

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
