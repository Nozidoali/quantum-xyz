#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:08:49
"""

from .QGate import QGate, QGateType
from .QBit import QBit

class BasicGate(QGate):
    """Class method for creating a gate .

    :param QGate: [description]
    :type QGate: [type]
    """
    def __init__(self, qgate_type: QGateType, target_qubit: QBit) -> None:
        QGate.__init__(self, qgate_type)

        if not isinstance(target_qubit, QBit):
            print(f"WARNING: target_qubit {target_qubit} is not a QBit")

        assert isinstance(target_qubit, QBit)
        self.target_qubit: QBit = target_qubit
