"""Shared data classes for the gate hierarchy: the enum, the qubit handle,
and the per-concern trait mixins that concrete gates compose in."""

from __future__ import annotations

from enum import Enum, auto
from typing import List

import numpy as np


class QGateType(Enum):
    U = auto()
    CU = auto()
    MCU = auto()

    X = auto()
    Y = auto()
    Z = auto()

    CY = auto()
    CZ = auto()
    CX = auto()

    RX = auto()
    RY = auto()
    RZ = auto()

    CRX = auto()
    CRY = auto()
    CRZ = auto()

    MCRY = auto()

    MULTIPLEX_Y = auto()

    MCMY = auto()

    NONE = auto()


class QBit:
    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f"q{self.index}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, QBit):
            return self.index == other.index
        return False

    def __hash__(self) -> int:
        return hash(self.index)


class RotationTrait:
    """Concrete gates with a single rotation angle `theta`."""

    def __init__(self, theta: float) -> None:
        self.theta = theta

    def is_trivial(self) -> bool:
        return np.isclose(self.theta, 0) or np.isclose(self.theta, 2 * np.pi)

    def is_pi(self) -> bool:
        return np.isclose(self.theta, np.pi) or np.isclose(self.theta, -np.pi)

    def get_theta(self) -> float:
        return self.theta


class UnitaryTrait:
    """Concrete gates parameterized by a 2×2 unitary matrix, with its
    Z-Y-Z decomposition pre-computed as `alpha`, `beta`, `gamma`."""

    def __init__(self, unitary: np.ndarray) -> None:
        self.unitary = unitary
        self.alpha, self.beta, self.gamma = _unitary_zyz_decomposition(unitary)

    def get_unitary(self) -> np.ndarray:
        return self.unitary

    def get_alpha(self) -> float:
        return self.alpha

    def get_beta(self) -> float:
        return self.beta

    def get_gamma(self) -> float:
        return self.gamma

    def is_z_trivial(self) -> bool:
        is_alpha_trivial = np.isclose(self.alpha, 0) or np.isclose(
            self.alpha, 2 * np.pi
        )
        is_gamma_trivial = np.isclose(self.gamma, 0) or np.isclose(
            self.gamma, 2 * np.pi
        )
        return is_alpha_trivial and is_gamma_trivial

    def is_z_trivial_not(self) -> bool:
        is_alpha_trivial = np.isclose(self.alpha, np.pi)
        is_gamma_trivial = np.isclose(self.gamma, np.pi)
        return is_alpha_trivial and is_gamma_trivial


class ControlledTrait:
    """Gates with exactly one control qubit and one control phase.
    Exposes `control_qubits` as a one-element list so callers can treat
    singly- and multi-controlled gates uniformly."""

    def __init__(self, control_qubit: QBit, phase: int = 1) -> None:
        assert isinstance(control_qubit, QBit)
        self.control_qubits: List[QBit] = [control_qubit]
        self.phase = phase

    @property
    def control_qubit(self) -> QBit:
        """Returns the (single) control qubit for backwards compatibility."""
        return self.control_qubits[0]

    def get_control_qubit(self) -> QBit:
        """Returns the control qubit."""
        return self.control_qubits[0]

    def get_control_qubits(self) -> List[QBit]:
        """Returns the control qubits."""
        return self.control_qubits

    def get_phase(self) -> int:
        """Returns the phase."""
        return self.phase

    def is_enabled(self, index: int) -> bool:
        q = self.control_qubits[0]
        return (index >> q.index) & 1 == self.phase


class MultiControlledTrait:
    """Gates with an arbitrary-length list of control qubits and phases."""

    def __init__(self, control_qubits: List[QBit], phases: List[int]) -> None:
        self.control_qubits: List[QBit] = list(control_qubits)
        self.phases: List[int] = list(phases)

    def has_zero_controls(self) -> bool:
        return len(self.control_qubits) == 0

    def has_one_control(self) -> bool:
        return len(self.control_qubits) == 1

    def get_control_qubits(self) -> List[QBit]:
        """Returns the control qubits."""
        return self.control_qubits

    def get_phases(self) -> List[int]:
        """Returns the phases."""
        return self.phases

    def is_enabled(self, index: int) -> bool:
        for ctrl, phase in zip(self.control_qubits, self.phases):
            if (index >> ctrl.index) & 1 != phase:
                return False
        return True

    def set_control_qubits(self, control_qubits: List[QBit]) -> None:
        self.control_qubits = list(control_qubits)

    def set_phases(self, phases: List[int]) -> None:
        self.phases = list(phases)


# --- ZYZ decomposition (moved out of qgate.py to break the trait / gate /
# decomposition circular dependency; Phase 3 will re-home this to
# xyz/decomposition/zyz.py).

def _to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    from numpy.linalg import det
    rank = matrix.shape[0]
    return matrix / det(matrix) ** (1 / rank)


def _unitary_zyz_decomposition(matrix: np.ndarray):
    """Return the Euler Z-Y-Z decomposition of a 1-qubit unitary."""
    U = _to_special_unitary(matrix)
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
