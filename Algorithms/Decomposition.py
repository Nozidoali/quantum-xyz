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

from qiskit import *
from qiskit.circuit.library.standard_gates import RYGate
import math

def find_thetas(alphas):
    size = len(alphas)
    # for the gray code matrix
    M = np.zeros((size, size))
    for i in range(size):
        for j in range(size):

            #  The exponent is the bit-wise inner product of the binary vectors for the standard binary code representation of the integer i (bi) and the binary representation of the i th value of the gray code up to a value of 2) The j th value of the gray code is calculated using the bit-wise XOR of the unsigned binary j and a single shift right of the value of j , like so: ”j XOR (j>>1)” for C++ code

            bitwise_inner_product = bin(i & (j ^ (j >> 1))).count('1')
            M[i, j] = (-1) ** bitwise_inner_product
    
    thetas = solve(M, alphas)

    # TODO: check the correctness of the thetas
    thetas = [ abs(theta) for theta in thetas ]

    return thetas

def decompose_multiple_controlled_rotation_Y_gate(matrix: np.ndarray, circuit: QuantumCircuit, control_qubits: list, target_qubit):

    num_qubits = len(control_qubits)
    
    alphas = 2 * np.arcsin( matrix.diagonal() )
    thetas = find_thetas(alphas)

    assert num_qubits == np.log2(len(thetas))

    for i, theta in enumerate(thetas):

        # get the number of gray code 
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i>>1)).count('1') - 1

        # CNOT
        if control_id >= 0:
            
            assert control_id < num_qubits
            circuit.cnot(control_qubits[control_id], target_qubit)

        # rotate the target qubit
        circuit.ry(theta, target_qubit)

    control_id = num_qubits - 1 # reset the control id
    circuit.cnot(control_qubits[control_id], target_qubit)

def decompose_multiple_controlled_rotation_Z_gate(matrix: np.ndarray, circuit: QuantumCircuit, control_qubits: list, target_qubit):

    num_qubits = len(control_qubits)
    
    alphas = -2 * -1j * np.log( matrix.diagonal() )
    thetas = find_thetas(alphas)

    assert num_qubits == np.log2(len(thetas))

    for i, theta in enumerate(thetas):

        # get the number of gray code 
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i>>1)).count('1') - 1

        # CNOT
        if control_id >= 0:
            
            assert control_id < num_qubits
            circuit.cnot(control_qubits[control_id], target_qubit)

        # rotate the target qubit
        circuit.rz(theta, target_qubit)

    control_id = num_qubits - 1 # reset the control id
    circuit.cnot(control_qubits[control_id], target_qubit)


def decompose_uniformly_controlled_gate(matrix: np.ndarray):

    dim = matrix.shape[0]
    half = int(dim / 2)
    
    matrix00 = matrix[: half, : half]
    matrix01 = matrix[: half, half :]
    matrix10 = matrix[half :, : half]
    matrix11 = matrix[half :, half :]

    # check if matrix01 and matrix10 are zero matrices
    # they should be zero matrices because they are uniformly controlled
    assert not np.any(matrix01) and not np.any(matrix10)

    matrix_product = matrix00 @ matrix11

    # eigenvalue decomposition
    eigenvalues, eigenvectors = eig(matrix_product)
    D = np.diag(np.sqrt(eigenvalues))
    V = eigenvectors
    V_inv = np.linalg.inv(V)
    W = D @ V_inv @ matrix11

    return D, V, W

def quantum_shannon_decomposition(matrix: np.ndarray) -> QCircuit:

    dim = matrix.shape[0]
    num_qubits = int(math.log(dim, 2))

    qr = QuantumRegister(num_qubits)
    cr = ClassicalRegister(num_qubits)
    circuit = QuantumCircuit(qr, cr)

    quantum_shannon_decomposition_helper(matrix, circuit, qr)
    circuit.measure(qr, cr)

    return circuit

def unitary_zyz_decomposition(matrix: np.ndarray, circuit, qubit) -> QCircuit:
    
    assert matrix.shape == (2, 2)

    # first cancel out the global phase
    phi = np.arctan(np.imag(det(matrix)) / np.real(det(matrix)))

    SU = np.exp(-1j * phi) * matrix

    A = SU[0, 0]
    B = SU[0, 1]

    sw = np.sqrt( np.real(A) ** 2 + np.imag(B) ** 2 + np.real(B) ** 2 )
    wx = np.imag(B) / sw
    wy = np.real(B) / sw
    wz = np.imag(A) / sw

    t1 = np.arctan( np.imag(A) / np.real(A) ) if np.real(A) != 0 else 0
    t2 = np.arctan( np.imag(B) / np.real(B) ) if np.real(B) != 0 else 0

    alpha = t1 + t2
    gamma = t1 - t2
    beta = 2 * np.arctan( sw * np.sqrt(wx**2 + wy**2) / np.sqrt(sw**2 + (wx*sw)**2) )

    assert alpha != np.NaN and beta != np.NaN and gamma != np.NaN

    circuit.rz(gamma, qubit)
    circuit.ry(beta, qubit)
    circuit.rz(alpha, qubit)

def quantum_shannon_decomposition_helper(matrix: np.ndarray, circuit, qubits: list):

    dim = matrix.shape[0]
    num_qubits = len(qubits)
    if num_qubits == 1:
        unitary_zyz_decomposition(matrix, circuit, qubits[0])
        return

    half = int(dim / 2)

    matrix00 = matrix[: half, : half]
    matrix01 = matrix[: half, half :]
    matrix10 = matrix[half :, : half]
    matrix11 = matrix[half :, half :]

    # step 1: cosine-sine decomposition
    U, CS, V = cossin((matrix00, matrix01, matrix10, matrix11))


    CS00 = CS[: half, : half]
    CS01 = CS[: half, half :]
    CS10 = CS[half :, : half]
    CS11 = CS[half :, half :]

    assert np.array_equal(CS00, CS11)
    assert np.array_equal(CS01, -CS10)

    C = CS00
    S = CS01

    # uniformly controlled gate decomposition
    U1, D, U2 = decompose_uniformly_controlled_gate(V)
    quantum_shannon_decomposition_helper(U2, circuit, qubits[1:])
    decompose_multiple_controlled_rotation_Z_gate(D, circuit, qubits[1:], qubits[0])
    quantum_shannon_decomposition_helper(U1, circuit, qubits[1:])

    decompose_multiple_controlled_rotation_Y_gate(S, circuit, qubits[1:], qubits[0])

    # uniformly controlled gate decomposition
    U1, D, U2 = decompose_uniformly_controlled_gate(U)
    quantum_shannon_decomposition_helper(U2, circuit, qubits[1:])
    decompose_multiple_controlled_rotation_Z_gate(D, circuit, qubits[1:], qubits[0])
    quantum_shannon_decomposition_helper(U1, circuit, qubits[1:])