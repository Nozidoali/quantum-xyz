#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 14:16:24
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 23:01:09
"""

import numpy as np
from numpy.linalg import det
from xyz.circuit import QCircuit
from xyz.Utils import *


def unitary_zyz_decomposition_legacy(matrix: np.ndarray) -> QCircuit:
    # https://quantumcomputing.stackexchange.com/questions/16256/what-is-the-procedure-of-finding-z-y-decomposition-of-unitary-matrices

    print(f"matrix = \n{matrix}")

    assert matrix.shape == (2, 2)

    # first cancel out the global phase
    # phi = np.arctan(np.imag(det(matrix)) / np.real(det(matrix)))

    SU = to_special_unitary(matrix)
    # SU = matrix

    print(f"SU = \n{SU}")

    A = SU[0, 0]
    B = SU[0, 1]
    C = SU[1, 0]
    D = SU[1, 1]

    phase = A * D - B * C
    # beta = np.arccos( np.real( np.sqrt(A*D/phase) ))
    beta = np.arctan2(np.absolute(B), np.absolute(A))

    if np.isclose(beta, 0.0, atol=1e-6):
        # basically, now alpha and gamma can be merged
        # also, no unique solution can be found
        beta = 0.0
        alpha = np.angle(D) - np.angle(A)
        gamma = 0.0
        return alpha, beta, gamma

    if np.isclose(beta, np.pi, atol=1e-6):
        # basically, now alpha and gamma can be merged
        # also, no unique solution can be found
        beta = np.pi
        alpha = np.angle(-B) + np.angle(C)
        gamma = 0.0
        return alpha, beta, gamma

    alpha = np.angle(C) - np.angle(A)
    gamma = np.angle(-B) - np.angle(A)

    return alpha, 2 * beta, gamma
