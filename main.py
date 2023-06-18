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
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, execute
from matplotlib import pyplot as plt
from qiskit.tools.visualization import plot_histogram

if __name__ == "__main__":

    U = np.identity(8, dtype=complex)
    U[:, 0] = np.array([0, 0, 0, 1, 0, 1, 1, 0]) * np.sqrt(3) / 3

    circuit = quantum_shannon_decomposition(U)

    simulator = Aer.get_backend('qasm_simulator')
    result = execute(circuit, backend=simulator).result()
    plot_histogram(result.get_counts(circuit))
    plt.show()
    exit(0)

    # print(circuit)
    with open('circuit.qasm', 'w') as f:
        f.write(circuit.qasm())

    circuit = zx.Circuit.from_qasm_file('circuit.qasm')
    g = circuit.to_basic_gates().to_graph()
    zx.simplify.full_reduce(g,quiet=True)
    new_circ = zx.extract_circuit(g)

    with open('circuit.qasm', 'w') as f:
        f.write(new_circ.to_basic_gates().to_qasm())

    circuit = QuantumCircuit.from_qasm_file('circuit.qasm')
    print(circuit)