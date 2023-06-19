#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-17 07:50:30
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 11:39:16
"""

from StatePreparator import *
from Algorithms import *
import pyzx as zx

import quantumflow as qf
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

if __name__ == "__main__":

    U = np.identity(8, dtype=complex)
    U[:, 0] = np.array([0, 0, 0, 1, 0, 1, 1, 0])
    U[:, 1] = np.array([1, 0, 0, 0, 0, 0, 0, 0])
    U = to_unitary(U)

    # U = np.kron(np.identity(4, dtype=complex), BasicGate.ry(np.pi/2))
    # U = np.kron(BasicGate.ry(np.pi/2), np.identity(4, dtype=complex) )


    # U = np.identity(4, dtype=complex)
    # c1 = np.array([[1, 0], [0, 0]])
    # c2 = np.array([[0, 0], [0, 1]])
    # U = np.kron(c1, np.identity(2)) + np.kron(c2, BasicGate.x())
    # U = to_unitary(U)

    # U = np.identity(4, dtype=complex)
    # U[:, 0] = np.array([1, 1, 1, 0])
    # U = to_unitary(U)

    # gate = qf.RandomGate(qubits=range(3))

    # circ = qf.translate(qf.quantum_shannon_decomposition(qf.UnitaryGate(U, range(3))))
    # circ = qf.translate(qf.quantum_shannon_decomposition(gate))
    # print(qf.circuit_to_diagram(circ))

    # circuit = qf.circuit_to_qiskit(circ)
    # print(circuit)

    # exit(0)

    # print(U)

    # circuit = quantum_shannon_decomposition(U)
    circuit = cofactor_decomposition(U[: , 0].flatten())
    print(circuit)

    circuit.simulate()
    exit(0)
    # exit(0)

    # print(circuit)
    with open("circuit.qasm", "w") as f:
        f.write(circuit.qasm())

    circuit = zx.Circuit.from_qasm_file("circuit.qasm")
    g = circuit.to_basic_gates().to_graph()
    zx.simplify.full_reduce(g, quiet=True)
    new_circ = zx.extract_circuit(g)

    with open("circuit.qasm", "w") as f:
        f.write(new_circ.to_basic_gates().to_qasm())

    circuit = QuantumCircuit.from_qasm_file("circuit.qasm")
    print(circuit)
