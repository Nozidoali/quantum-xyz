#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-13 10:29:30
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 10:33:49
"""

# pylint: disable=C0103

import numpy as np

from .base import BasicGate, QBit, QGateType, UnitaryGate


class U(UnitaryGate, BasicGate):
    """Constructs a Unitary gate .

    :param RotationGate: [description]
    :type RotationGate: [type]
    :param BasicGate: [description]
    :type BasicGate: [type]
    """

    def __init__(self, unitary: np.ndarray, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.U, target_qubit)
        UnitaryGate.__init__(self, unitary)

    def __str__(self) -> str:
        return "U"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 0

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("This method is not implemented")
