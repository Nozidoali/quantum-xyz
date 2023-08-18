#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 20:14:09
"""

from .base import BasicGate, QGateType, QBit


class Z(BasicGate):
    """Classmethod to create a Gate class .

    :param BasicGate: [description]
    :type BasicGate: [type]
    """

    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.Z, target_qubit)

    def __str__(self) -> str:
        return f"Z({self.target_qubit})"
