#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-13 10:30:05
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 10:31:53
"""

from scipy.linalg import det

import numpy as np


def to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    """Convert gate tensor to the special unitary group."""
    rank = matrix.shape[0]
    matrix_ = matrix / det(matrix) ** (1 / rank)
    return matrix_


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


class UnitaryGate:
    """Classmethod to handle RotationGate ."""

    def __init__(self, unitary: np.ndarray) -> None:
        self.unitary = unitary

        self.alpha, self.beta, self.gamma = unitary_zyz_decomposition(unitary)

    def get_unitary(self) -> float:
        """Get the theta of the rotation gate .

        :return: [description]
        :rtype: float
        """
        return self.unitary

    def get_alpha(self) -> float:
        """Get the theta of the rotation gate .

        :return: [description]
        :rtype: float
        """
        return self.alpha

    def get_beta(self) -> float:
        """Get the theta of the rotation gate .

        :return: [description]
        :rtype: float
        """
        return self.beta

    def get_gamma(self) -> float:
        """Get the theta of the rotation gate .

        :return: [description]
        :rtype: float
        """
        return self.gamma

    def is_z_trivial(self) -> bool:
        """Whether the model is trivial to be trivial .

        :return: [description]
        :rtype: bool
        """
        is_alpha_trivial = np.isclose(self.alpha, 0) or np.isclose(
            self.alpha, 2 * np.pi
        )
        is_gamma_trivial = np.isclose(self.gamma, 0) or np.isclose(
            self.gamma, 2 * np.pi
        )

        return is_alpha_trivial and is_gamma_trivial

    def is_z_trivial_not(self) -> bool:
        """Whether z - T is z - T .

        :return: [description]
        :rtype: bool
        """
        is_alpha_trivial = np.isclose(self.alpha, np.pi)
        is_gamma_trivial = np.isclose(self.gamma, np.pi)

        return is_alpha_trivial and is_gamma_trivial
