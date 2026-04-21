"""Single-qubit concrete gates: X, Z, RX, RY, RZ, U."""

from __future__ import annotations

from typing import List

import numpy as np

from xyz.state.qstate import QState
from xyz.gates.base import BasicGate
from xyz.gates.types import QBit, QGateType, RotationTrait, UnitaryTrait


class X(BasicGate):
    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.X, target_qubit)

    def __str__(self) -> str:
        return f"X({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx in qstate.index_set:
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            index_to_weight[reversed_idx] = qstate.index_to_weight[idx]
        return QState(index_to_weight, qstate.num_qubits)


class Z(BasicGate):

    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.Z, target_qubit)

    def __str__(self) -> str:
        return f"Z({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx, weight in qstate.index_to_weight.items():
            if idx & (1 << self.target_qubit.index):
                index_to_weight[idx] = -weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, qstate.num_qubits)


class RX(RotationTrait, BasicGate):

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RX, target_qubit)
        RotationTrait.__init__(self, theta)

    def __str__(self) -> str:
        return f"RX({self.theta:0.02f})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # Real projection of RX(θ) on a real-amplitude state is scalar
        # multiplication by cos(θ/2). See Phase 2 plan Task 5 math note.
        scale = float(np.cos(self.theta / 2))
        return QState(
            {idx: w * scale for idx, w in qstate.index_to_weight.items()},
            qstate.num_qubits,
        )


class RY(RotationTrait, BasicGate):

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RY, target_qubit)
        RotationTrait.__init__(self, theta)

    def __str__(self) -> str:
        return f"RY({self.target_qubit}, {self.theta:0.02f})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def conjugate(self) -> "RY":
        return RY(-self.theta, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {idx: 0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
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


class RZ(RotationTrait, BasicGate):
    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RZ, target_qubit)
        RotationTrait.__init__(self, theta)

    def __str__(self) -> str:
        return f"RZ({self.theta:0.02f})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # RZ's real projection on a real-amplitude state matches RX's:
        # both reduce to cos(θ/2)·ψ. See Phase 2 plan Task 5 math note.
        scale = float(np.cos(self.theta / 2))
        return QState(
            {idx: w * scale for idx, w in qstate.index_to_weight.items()},
            qstate.num_qubits,
        )


class U(UnitaryTrait, BasicGate):
    def __init__(self, unitary: np.ndarray, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.U, target_qubit)
        UnitaryTrait.__init__(self, unitary)

    def __str__(self) -> str:
        return "U"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # Apply Re(U) as a 2×2 real matrix on the two-amplitude subspace
        # indexed by the target qubit's bit.
        m = np.real(self.unitary)
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
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
