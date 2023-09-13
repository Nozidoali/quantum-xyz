#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-13 10:25:48
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 10:26:14
"""

from .base import BasicGate, ControlledGate, QBit, QGateType, RotationGate


class CRZ(RotationGate, BasicGate, ControlledGate):
    """Classmethod to create CRZ and ControlledGate gate .

    :param RotationGate: [description]
    :type RotationGate: [type]
    :param BasicGate: [description]
    :type BasicGate: [type]
    :param ControlledGate: [description]
    :type ControlledGate: [type]
    """

    def __init__(
        self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CRZ, target_qubit)
        RotationGate.__init__(self, theta)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"CRZ({self.theta:0.02f}, {self.control_qubit}[{self.phase}])"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 2
