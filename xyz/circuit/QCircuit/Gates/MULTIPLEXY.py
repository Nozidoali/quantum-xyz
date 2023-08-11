#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 23:55:57
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 00:13:28
"""

from .Base import AdvancedGate, QBit, QGateType


class MULTIPLEXY(AdvancedGate):
    """Returns a DanceXRULTI class .

    :param AdvancedGate: [description]
    :type AdvancedGate: [type]
    """

    def __init__(
        self, theta0: float, theta1: float, control_qubit: QBit, target_qubit: QBit
    ) -> None:
        AdvancedGate.__init__(self, QGateType.MULTIPLEX_Y)

        assert isinstance(target_qubit, QBit)
        assert isinstance(control_qubit, QBit)

        self.target_qubit: QBit = target_qubit
        self.control_qubit: QBit = control_qubit
        self.theta0: float = theta0
        self.theta1: float = theta1

    def __str__(self) -> str:
        return f"MULTIPLEXY({self.theta0}, {self.theta1}, {self.control_qubit}, {self.target_qubit})"
