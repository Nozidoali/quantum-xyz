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
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

if __name__ == "__main__":
    state = D_state(5, 2)
    # state = W_state(6)
    # state = GHZ_state(4)
    # print(''.join([str(int(x > 0)) for x in state[:]])[::-1])

    circuit = cofactor_decomposition(state)

    # TODO: buggy, need to fix
    if False:
        U = np.identity(8, dtype=complex)
        U[:, 0] = np.array([0, 1, 1, 0, 1, 0, 0, 0])
        U[:, 1] = np.array([1, 0, 0, 0, 0, 0, 0, 0])
        U = to_unitary(U)
        circuit = quantum_shannon_decomposition(U)

    # circuit.circuit.add_bits(QuantumRegister(1, 'ancilla'))
    # circuit.circuit.add_register(QuantumRegister(1, 'ancilla'))

    print(circuit)
    circuit.simulate()

    print(circuit.circuit.count_ops()["cx"])

    # circuit.simulate()
    with open("./tmp/circuit.qasm", "w") as f:
        f.write(circuit.qasm())
