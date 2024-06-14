#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 11:32:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 11:32:58
"""

# https://stackoverflow.com/questions/47561840/how-can-i-separate-the-functions-of-a-class-into-multiple-files


# standard library
from typing import List

# internal modules
from .gate import QGate, QGateType, QBit
from ._optimization import _add_gate_optimized, _add_gates_optimized

class QCircuit:
    """the class of quantum circuit"""

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
        _add_gate_optimized(self, gate)

    def add_gates(self, gates: List[QGate]):
        _add_gates_optimized(self, gates)

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
