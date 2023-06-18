#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 11:30:04
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 11:47:11
"""

import numpy as np
from scipy.linalg import cossin, eig, solve, det
from scipy.stats import unitary_group
from Circuit import QCircuit

from Algorithms.Decompose import *

from qiskit.circuit.library.standard_gates import RYGate
import math


def quantum_shannon_decomposition(matrix: np.ndarray) -> QCircuit:

    dim = matrix.shape[0]
    num_qubits = int(math.log(dim, 2))

    circuit = QCircuit(num_qubits)

    quantum_shannon_decomposition_helper(matrix, circuit, circuit.qr)
    circuit.flush()
    circuit.measure()
    return circuit


def quantum_shannon_decomposition_helper(matrix: np.ndarray, circuit, qubits: list):

    dim = matrix.shape[0]
    num_qubits = len(qubits)
    if num_qubits == 1:
        qubit = qubits[0]
        alpha, beta, gamma = unitary_zyz_decomposition(matrix)

        if not np.isclose(gamma, 0.0):
            circuit.rz(gamma, qubit)
        if not np.isclose(beta, 0.0):
            circuit.ry(beta, qubit)
        if not np.isclose(alpha, 0.0):
            circuit.rz(alpha, qubit)
        return

    half = int(dim / 2)

    matrix00 = matrix[:half, :half]
    matrix01 = matrix[:half, half:]
    matrix10 = matrix[half:, :half]
    matrix11 = matrix[half:, half:]

    # step 1: cosine-sine decomposition
    U, CS, V = cossin((matrix00, matrix01, matrix10, matrix11))

    CS00 = CS[:half, :half]
    CS01 = CS[:half, half:]
    CS10 = CS[half:, :half]
    CS11 = CS[half:, half:]

    assert np.array_equal(CS00, CS11)
    assert np.array_equal(CS01, -CS10)
    assert np.allclose(U @ CS @ V, matrix)

    C = CS00
    S = CS01

    # uniformly controlled gate decomposition
    D, U1, U2 = decompose_uniformly_controlled_gate(V)
    quantum_shannon_decomposition_helper(U2, circuit, qubits[1:])
    decompose_multiple_controlled_rotation_Z_gate(D, circuit, qubits[1:], qubits[0])
    quantum_shannon_decomposition_helper(U1, circuit, qubits[1:])

    decompose_multiple_controlled_rotation_Y_gate(S, circuit, qubits[1:], qubits[0])

    # uniformly controlled gate decomposition
    D, U1, U2 = decompose_uniformly_controlled_gate(U)
    quantum_shannon_decomposition_helper(U2, circuit, qubits[1:])
    decompose_multiple_controlled_rotation_Z_gate(D, circuit, qubits[1:], qubits[0])
    quantum_shannon_decomposition_helper(U1, circuit, qubits[1:])
