"""Z-Y-Z Euler decomposition of a 1-qubit unitary."""

from __future__ import annotations

import numpy as np
from numpy.linalg import det


def to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    """Normalize a unitary matrix to have determinant 1 (SU(2))."""
    rank = matrix.shape[0]
    return matrix / det(matrix) ** (1 / rank)


def unitary_zyz_decomposition(matrix: np.ndarray):
    """Return the Euler Z-Y-Z decomposition of a 1-qubit unitary.

    Returns a tuple (theta0, theta1, theta2) where the gate equals
    R_z(theta2) @ R_y(theta1) @ R_z(theta0) up to a global phase.
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
