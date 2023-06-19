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

    state = D_state(4,2)
    # state = W_state(15)
    # state = GHZ_state(4)

    print(state)
    circuit = cofactor_decomposition(state)

    # TODO: buggy, need to fix
    if False:
        U = np.identity(8, dtype=complex)
        U[:, 0] = np.array([0, 1, 1, 0, 1, 0, 0, 0])
        U[:, 1] = np.array([1, 0, 0, 0, 0, 0, 0, 0])
        U = to_unitary(U)
        circuit = quantum_shannon_decomposition(U)

    print(circuit)

    circuit.simulate()
    with open("./tmp/circuit.qasm", "w") as f:
        f.write(circuit.qasm())
    # exit(0)
    # exit(0)

    # print(circuit)

    # circuit = zx.Circuit.from_qasm_file("./tmp/circuit.qasm")
    # g = circuit.to_basic_gates().to_graph()
    # zx.simplify.full_reduce(g, quiet=True)
    # new_circ = zx.extract_circuit(g)

    # with open("./tmp/circuit_opt.qasm", "w") as f:
    #     f.write(new_circ.to_basic_gates().to_qasm())

    # circuit = QuantumCircuit.from_qasm_file("./tmp/circuit_opt.qasm")
    # print(circuit)
