#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:14:28
"""

from .Base import BasicGate, ControlledGate, QBit, QGateType


class CX(BasicGate, ControlledGate):
    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        return f"CX({self.control_qubit}, {self.target_qubit}) {self.phase}"
