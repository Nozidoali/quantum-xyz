#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:22:18
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:43:20
"""

from typing import List
from .Gates import *

import llist
from llist import dllist


class QCircuitBase:
    def __init__(self) -> None:
        self.__gates: List[QGate] = []
        self.__qubits: List[QBit] = []

    def get_num_qubits(self) -> int:
        """
        Get the number of qubits in the circuit
        """
        return len(self.__qubits)

    def qubit_at(self, index: int) -> QBit:
        """
        Get the qubit at the specified index
        """
        return self.__qubits[index]

    def get_gates(self) -> List[QGate]:
        """
        Get the gates in the circuit
        """
        return self.__gates

    def add_gate(self, gate: QGate):
        """
        Add a gate to the circuit
        """
        self.__gates.append(gate)

    def add_gates(self, gates: List[QGate]):
        """
        Add a list of gates to the circuit
        """
        self.__gates.extend(gates)

    def add_qubit(self, qubit: QBit):
        """
        Add a qubit to the circuit
        """
        self.__qubits.append(qubit)

    def add_qubits(self, qubits: List[QBit]):
        """
        Add a list of qubits to the circuit
        """
        self.__qubits.extend(qubits)

    def init_qubits(self, num_qubits: int):
        """
        Add a list of qubits to the circuit
        """
        for i in range(num_qubits):
            self.add_qubit(QBit(i))

    def num_gates(self, gate_type: QGateType = None) -> int:
        """
        Get the number of gates in the circuit
        """
        if gate_type is None:
            return len(self.__gates)
        else:
            return len([gate for gate in self.__gates if gate.get_type() == gate_type])