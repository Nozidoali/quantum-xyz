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
from Circuit.QCircuit import QCircuit
from Util import *


def unitary_zyz_decomposition(matrix: np.ndarray):
    """
    Returns the Euler Z-Y-Z decomposition of a local 1-qubit gate.
    """

    U = to_special_unitary(matrix)

    if abs(U[0, 0]) > abs(U[1, 0]):
        theta1 = 2 * np.arccos(min(abs(U[0, 0]), 1))
    else:
        theta1 = 2 * np.arcsin(min(abs(U[1, 0]), 1))

    cos_halftheta1 = np.cos(theta1 / 2)
    if not np.isclose(cos_halftheta1, 0.0):
        phase = U[1, 1] / cos_halftheta1
        theta0_plus_theta2 = 2 * np.arctan2(np.imag(phase), np.real(phase))
    else:
        theta0_plus_theta2 = 0.0

    sin_halftheta1 = np.sin(theta1 / 2)
    if not np.isclose(sin_halftheta1, 0.0):
        phase = U[1, 0] / sin_halftheta1
        theta0_sub_theta2 = 2 * np.arctan2(np.imag(phase), np.real(phase))
    else:
        theta0_sub_theta2 = 0.0

    theta0 = (theta0_plus_theta2 + theta0_sub_theta2) / 2
    theta2 = (theta0_plus_theta2 - theta0_sub_theta2) / 2

    # this is very important, otherwise the result will be wrong
    # TODO: find a better value of atol
    if np.isclose(theta1, 0.0, atol=1e-6):
        theta2 = theta0 + theta2
        theta1 = 0.0
        theta0 = 0.0

    if theta0 < 0:
        theta0 += 2 * np.pi
    if theta1 < 0:
        theta1 += 2 * np.pi
    if theta2 < 0:
        theta2 += 2 * np.pi

    return theta0, theta1, theta2

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
    
    phase = A*D - B*C
    # beta = np.arccos( np.real( np.sqrt(A*D/phase) ))
    beta = np.arctan2( np.absolute(B), np.absolute(A) )

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