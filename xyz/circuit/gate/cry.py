#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:32:05
"""

import numpy as np

from .base import BasicGate, ControlledGate, QBit, QGateType, RotationGate
from .qstate import QState


class CRY(RotationGate, BasicGate, ControlledGate):
    """Controlled Y Rotation."""

    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRY, target_qubit)
        RotationGate.__init__(self, theta)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        control_str = "" if self.phase == 1 else "~"
        return f"C({control_str}{self.control_qubit})RY({self.target_qubit}:{self.theta:0.02f})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate."""
        return 2

    def conjugate(self) -> "CRY":
        return CRY(-self.theta, self.control_qubit, self.phase, self.target_qubit)

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
