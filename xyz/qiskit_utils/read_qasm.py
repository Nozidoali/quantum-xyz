#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-22 17:42:50
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-22 17:53:19
"""

from ..circuit import QCircuit, QGate, QBit, X, RY, CX
from qiskit import qasm3, QuantumCircuit, QuantumRegister


def read_qasm(filename: str) -> QCircuit:
    """
    read_qasm:
    read a qasm file and return the corresponding QCircuit object
    """
    with open(filename, "r") as f:
        program = f.read()
    qc = qasm3.loads(program)

    # convert qc to QCircuit
    n_qubits = qc.num_qubits
    circuit = QCircuit(n_qubits)

    for instr, qargs, cargs in qc.data:
        gate: QGate = None

        if instr.name == "x":
            gate = X(QBit(qargs[0]._index))
        elif instr.name == "ry":
            gate = RY(instr.params[0], QBit(qargs[0]._index))
        elif instr.name == "cx":
            gate = CX(QBit(qargs[0]._index), True, QBit(qargs[1]._index))
        else:
            raise ValueError(f"Unsupported instruction {instr.name}")

        circuit.add_gate(gate)
    return circuit
