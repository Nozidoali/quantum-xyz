#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:14:11
"""

# pylint: disable=C0103

from .qstate import QState
from .base import BasicGate, QBit, QGateType


class X(BasicGate):
    """Class method for creating a X gate class .

    :param BasicGate: [description]
    :type BasicGate: [type]
    """

    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.X, target_qubit)

    def __str__(self) -> str:
        return f"X({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 0

    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx in qstate.index_set:
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            index_to_weight[reversed_idx] = qstate.index_to_weight[idx]
        return QState(index_to_weight, qstate.num_qubits)
