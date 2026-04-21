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


class UnitaryTrait:
    """Concrete gates parameterized by a 2×2 unitary matrix, with its
    Z-Y-Z decomposition pre-computed as `alpha`, `beta`, `gamma`."""

    def __init__(self, unitary: np.ndarray) -> None:
        self.unitary = unitary
        from xyz.decomposition.zyz import unitary_zyz_decomposition
        self.alpha, self.beta, self.gamma = unitary_zyz_decomposition(unitary)

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

    def is_enabled(self, index: int) -> bool:
        for ctrl, phase in zip(self.control_qubits, self.phases):
            if (index >> ctrl.index) & 1 != phase:
                return False
        return True
