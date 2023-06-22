#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 11:32:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 11:32:58
"""

from qiskit import *
from qiskit import Aer, execute
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from matplotlib import pyplot as plt
from qiskit.tools.visualization import plot_histogram

import numpy as np
from typing import List
from qiskit.circuit.library.standard_gates import *


from .Gates.Base.QGate import *
from .Gates.Base.QBit import *
from .QCircuitBase import *
from .QCircuitQiskitCompatible import *

class QCircuitParams:
    has_mcry: bool = False

class QCircuit(QCircuitQiskitCompatible):
    def __init__(self, num_qubits):

        super().__init__()
        self.init_qubits(num_qubits)

        # TODO: make all the attributes private

        self.num_qubits = num_qubits

        self.qr = QuantumRegister(num_qubits)
        self.cr = ClassicalRegister(num_qubits)
        self.circuit = QuantumCircuit(self.qr, self.cr)

        self.gates: list = []

        self.cnot_queue: list = []

        self.cnot_controls: dict = {qubit: 0 for qubit in self.qr}
        self.cnot_targets: dict = {qubit: 0 for qubit in self.qr}

        self.structural_hashing: bool = True
        self.enable_cnot_queue: bool = True

        self.max_ancilla_qubits: int = 1

        self.ancilla_qubits = []


    def has_mcry(self):
        return QCircuitParams.has_mcry
    
    def mcry(self, theta, control_qubits, target_qubit):
        if np.isclose(theta, 0) and self.structural_hashing:
            return False
        
        if len(control_qubits) == 0:
            self.circuit.ry(theta, target_qubit)
            return True

        num_control_qubits = len(control_qubits)
        qubits, phases = zip(*control_qubits)

        # we need to reverse the order of the control qubits
        # because the qiskit's control gate is in the reverse order
        control_str = ''.join([str(int(phase)) for phase in phases])[::-1]

        # print("control_str: ", control_str)
        # print("qubits: ", qubits)
        
        mcry_gate=RYGate(theta).control(num_control_qubits, ctrl_state=control_str)

        if self.enable_cnot_queue:
            if (
                self.cnot_controls[target_qubit] > 0
                or self.cnot_targets[target_qubit] > 0
            ):
                self.flush_cnot_queue()
            
            for qubit in qubits:
                if self.cnot_controls[qubit] > 0 or self.cnot_targets[qubit] > 0:
                    self.flush_cnot_queue()
                    break

        self.circuit.append(mcry_gate, qubits + (target_qubit,))
        return True

    def measure(self):
        self.circuit.measure(self.qr, self.cr)

    def rz(self, theta, qubit):
        if np.isclose(theta, 0) and self.structural_hashing:
            return False

        if self.enable_cnot_queue:
            if self.cnot_controls[qubit] > 0 or self.cnot_targets[qubit] > 0:
                self.flush_cnot_queue()

        self.circuit.rz(theta, qubit)
        return True

    def ry(self, theta, qubit):
        if np.isclose(theta, 0) and self.structural_hashing:
            return False

        if self.enable_cnot_queue:
            if self.cnot_controls[qubit] > 0 or self.cnot_targets[qubit] > 0:
                self.flush_cnot_queue()

        self.circuit.ry(theta, qubit)
        return True

    def cx(self, control_qubit, target_qubit):

        assert (
            control_qubit != target_qubit
        ), "control qubit and target qubit cannot be the same"

        if self.enable_cnot_queue:

            if (
                self.cnot_controls[target_qubit] > 0
                or self.cnot_targets[control_qubit] > 0
            ):
                # then we need to flush the queue
                # because the two operators are not commute
                for control, target in self.cnot_queue:
                    self.circuit.cx(control, target)
                    self.cnot_controls[control] -= 1
                    self.cnot_targets[target] -= 1
                self.cnot_queue.clear()

            else:
                # check if the current cnot is in the queue
                if (control_qubit, target_qubit) in self.cnot_queue:

                    # we don't need to add this cnot to the queue
                    # because it is already in the queue
                    # besides, we can remove it from the queue
                    self.cnot_queue.remove((control_qubit, target_qubit))

                    self.cnot_controls[control_qubit] -= 1
                    self.cnot_targets[target_qubit] -= 1
                    return False

                self.cnot_controls[control_qubit] += 1
                self.cnot_targets[target_qubit] += 1
                self.cnot_queue.append((control_qubit, target_qubit))

        else:
            self.circuit.cx(control_qubit, target_qubit)

        return True

    def flush(self):
        self.flush_cnot_queue()

    def flush_cnot_queue(self):
        for control, target in self.cnot_queue:
            self.circuit.cx(control, target)
            self.cnot_controls[control] -= 1
            self.cnot_targets[target] -= 1
        self.cnot_queue.clear()

    def simulate(self):
        simulator = Aer.get_backend("qasm_simulator")
        result = execute(self.circuit, backend=simulator, shots=2 ** 14).result()
        return result.get_counts(self.circuit)
        # plot_histogram(result.get_counts(self.circuit))
        # plt.show()

    def __str__(self) -> str:
        return self.circuit.__str__()

    def qasm(self):
        return self.circuit.qasm()
