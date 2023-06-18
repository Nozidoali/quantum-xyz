#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 16:04:20
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 21:28:17
"""

import numpy as np
from scipy.linalg import eig


def decompose_uniformly_controlled_gate(matrix: np.ndarray):

    dim = matrix.shape[0]
    half = int(dim / 2)

    #
    # matrix:
    #  |          |          |
    #  | matrix00 | matrix01 |
    #  |          |          |
    #  |----------|----------|
    #  |          |          |
    #  | matrix10 | matrix11 |
    #  |          |          |
    #
    matrix00 = matrix[:half, :half]
    matrix01 = matrix[:half, half:]
    matrix10 = matrix[half:, :half]
    matrix11 = matrix[half:, half:]

    # check if matrix01 and matrix10 are zero matrices
    # they should be zero matrices because they are uniformly controlled
    assert not np.any(matrix01) and not np.any(matrix10)

    matrix_product = matrix00 @ matrix11.conj().T

    # eigenvalue decomposition
    eigenvalues, eigenvectors = eig(matrix_product)
    D = np.diag(np.sqrt(eigenvalues))
    V = eigenvectors
    V_inv = V.conj().T
    W = D @ V_inv @ matrix11

    # identity matrix
    c1 = np.array([[1, 0], [0, 0]])
    c2 = np.array([[0, 0], [0, 1]])

    print(f"matrix \n {matrix}")

    V_matrix = np.kron(np.identity(2), V)
    W_matrix = np.kron(np.identity(2), W)
    D_matrix = np.kron(c1, D) + np.kron(c2, D.conj().T)

    if not np.allclose(V_matrix @ D_matrix @ W_matrix, matrix):

        diff = matrix @ (V_matrix @ D_matrix @ W_matrix).conj().T

        print(f"difference \n {diff}")

    assert np.allclose(V_matrix @ D_matrix @ W_matrix, matrix)

    return D, V, W
