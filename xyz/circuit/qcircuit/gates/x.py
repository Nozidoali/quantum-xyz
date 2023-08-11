#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:14:11
"""

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
