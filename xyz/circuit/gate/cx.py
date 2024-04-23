#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:14:28
"""

from .qstate import QState
from .base import BasicGate, ControlledGate, QBit, QGateType


class CX(BasicGate, ControlledGate):
    """Classmethod to create a CX and ControlledGate .

    :param BasicGate: [description]
    :type BasicGate: [type]
    :param ControlledGate: [description]
    :type ControlledGate: [type]
    """

    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubit})X({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 1

    def conjugate(self) -> "CX":
        """Return the conjugate of the gate .

        :return: [description]
        :rtype: CX
        """
        return CX(self.control_qubit, self.phase, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx, weight in qstate.index_to_weight.items():
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            if self.is_enabled(idx):
                index_to_weight[reversed_idx] = weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, qstate.num_qubits)
