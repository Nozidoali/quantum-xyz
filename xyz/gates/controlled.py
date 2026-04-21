"""Singly-controlled concrete gates: CX, CRX, CRY, CRZ, CU."""

from __future__ import annotations

from typing import List

import numpy as np

from xyz.circuit.qstate import QState
from xyz.gates.base import BasicGate
from xyz.gates.types import (
    ControlledTrait,
    QBit,
    QGateType,
    RotationTrait,
    UnitaryTrait,
)


class CRX(RotationTrait, BasicGate, ControlledTrait):
    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRX, target_qubit)
        RotationTrait.__init__(self, theta)
        ControlledTrait.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"CRX({self.theta:0.02f}, {self.control_qubits[0]}[{self.phase}])"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        scale = float(np.cos(self.theta / 2))
        out = {}
        for idx, weight in qstate.index_to_weight.items():
            out[idx] = weight * scale if self.is_enabled(idx) else weight
        return QState(out, qstate.num_qubits)


class CRY(RotationTrait, BasicGate, ControlledTrait):
    """Controlled Y Rotation."""

    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRY, target_qubit)
        RotationTrait.__init__(self, theta)
        ControlledTrait.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        control_str = "" if self.phase == 1 else "~"
        return f"C({control_str}{self.control_qubits[0]})RY({self.target_qubit}:{self.theta:0.02f})"

    def cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate."""
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def conjugate(self) -> "CRY":
        return CRY(-self.theta, self.control_qubits[0], self.phase, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {idx: 0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            # no rotation
            if not self.is_enabled(idx):
                index_to_weight[idx] = qstate.index_to_weight[idx]
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0

            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] += weight * np.sin(self.theta / 2)
            else:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] -= weight * np.sin(self.theta / 2)
        return QState(index_to_weight, qstate.num_qubits)


class CRZ(RotationTrait, BasicGate, ControlledTrait):

    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRZ, target_qubit)
        RotationTrait.__init__(self, theta)
        ControlledTrait.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"CRZ({self.theta:0.02f}, {self.control_qubits[0]}[{self.phase}])"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        scale = float(np.cos(self.theta / 2))
        out = {}
        for idx, weight in qstate.index_to_weight.items():
            out[idx] = weight * scale if self.is_enabled(idx) else weight
        return QState(out, qstate.num_qubits)


class CU(BasicGate, UnitaryTrait, ControlledTrait):

    def __init__(
        self, unitary: np.ndarray, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CU, target_qubit)
        UnitaryTrait.__init__(self, unitary)
        ControlledTrait.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubits[0]})U({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 2

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def apply(self, qstate: "QState") -> "QState":
        m = np.real(self.unitary)
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            if not self.is_enabled(idx):
                index_to_weight[idx] += weight
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * m[0, 0]
                index_to_weight[rdx] += weight * m[1, 0]
            else:
                index_to_weight[idx] += weight * m[1, 1]
                index_to_weight[rdx] += weight * m[0, 1]
        return QState(index_to_weight, qstate.num_qubits)


class CX(BasicGate, ControlledTrait):

    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledTrait.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubits[0]})X({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 1

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)

    def conjugate(self) -> "CX":
        return CX(self.control_qubits[0], self.phase, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx, weight in qstate.index_to_weight.items():
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            if self.is_enabled(idx):
                index_to_weight[reversed_idx] = weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, qstate.num_qubits)
