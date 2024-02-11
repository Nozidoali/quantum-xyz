#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-27 00:18:14
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-27 00:39:26
"""

import numpy as np

from typing import Any
from xyz.qstate import QState

from .operator import QOperatorBase, QOperatorType
from .rotation import QuantizedRotation, QuantizedRotationType


class TROperator(QOperatorBase, QuantizedRotation):
    """Creates an TROperator class with TROperator .

    :param QOperatorBase: [description]
    :type QOperatorBase: [type]
    :param QuantizedRotation: [description]
    :type QuantizedRotation: [type]
    """

    def __init__(
        self,
        target_qubit_index: int,
        target_phase: bool,
    ) -> None:
        if target_phase is True:
            QOperatorBase.__init__(self, QOperatorType.T1, target_qubit_index)
            QuantizedRotation.__init__(self, QuantizedRotationType.MERGE1)
        else:
            QOperatorBase.__init__(self, QOperatorType.T0, target_qubit_index)
            QuantizedRotation.__init__(self, QuantizedRotationType.MERGE0)

        # The angle of the rotation.
        self.theta = None

    def __call__(self, qstate: QState) -> Any:
        """
        This method is used to apply a quantum gate operation to a quantum state.
        @param qstate - The input quantum state.
        @return The modified quantum state after applying the gate operation.
        """
        if self.operator_type == QOperatorType.T0:
            next_state, theta = qstate.apply_merge0(self.target_qubit_index)
            self.theta = theta
            return next_state
        if self.operator_type == QOperatorType.T1:
            next_state, theta = qstate.apply_merge1(self.target_qubit_index)
            # this is an interesting case, we need to rotate to the opposite direction
            self.theta = theta - np.pi  # we need to rotate another pi
            return next_state

    def __str__(self) -> str:
        """The repr of the class .

        :return: [description]
        :rtype: str
        """
        target_phase_str = "1" if self.operator_type == QOperatorType.T1 else "0"

        return f"TR({self.target_qubit_index}->{target_phase_str})"

    def get_cost(self) -> int:
        """Returns the cost of the job .

        :return: [description]
        :rtype: int
        """
        return 0
