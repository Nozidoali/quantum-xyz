#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 20:14:09
"""

from .base import BasicGate, QGateType, QBit

# pylint: disable=C0103


class Z(BasicGate):
    """Classmethod to create a Gate class .

    :param BasicGate: [description]
    :type BasicGate: [type]
    """

    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.Z, target_qubit)

    def __str__(self) -> str:
        return f"Z({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 0

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("Z gate not implemented")
