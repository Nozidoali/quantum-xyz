#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:14:28
"""

from .base import BasicGate, ControlledGate, QBit, QGateType


class CX(BasicGate, ControlledGate):
    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"C({self.control_qubit} = {self.phase})X({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 1