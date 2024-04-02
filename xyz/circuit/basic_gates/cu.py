#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-13 10:29:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 10:43:53
"""

import numpy as np

from .base import BasicGate, UnitaryGate, ControlledGate, QBit, QGateType


class CU(BasicGate, UnitaryGate, ControlledGate):
    """Classmethod to create a CU and ControlledGate .

    :param BasicGate: [description]
    :type BasicGate: [type]
    :param ControlledGate: [description]
    :type ControlledGate: [type]
    """

    def __init__(
        self, unitary: np.ndarray, control_qubit: QBit, phase: int, target_qubit: QBit
    ) -> None:
        BasicGate.__init__(self, QGateType.CU, target_qubit)
        UnitaryGate.__init__(self, unitary)
        ControlledGate.__init__(self, control_qubit, phase)

    def __str__(self) -> str:
        phase_str = "" if self.phase == 1 else "~"
        return f"C({phase_str}{self.control_qubit})U({self.target_qubit})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 2

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("CU gate is not implemented yet")
