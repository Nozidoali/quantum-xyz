#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:03:19
"""

from .base import BasicGate, QBit, QGateType, RotationGate


class RY(RotationGate, BasicGate):
    """Constructs a RYYY gate .

    :param RotationGate: [description]
    :type RotationGate: [type]
    :param BasicGate: [description]
    :type BasicGate: [type]
    """

    def __init__(self, theta: float, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.RY, target_qubit)
        RotationGate.__init__(self, theta)

    def __str__(self) -> str:
        return f"RY({self.theta:0.02f})"
