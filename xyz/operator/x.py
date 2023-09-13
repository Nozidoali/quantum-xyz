#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:36:46
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:42:30
"""

from typing import Any

from xyz.qstate import QState

from .operator import QOperatorBase, QOperatorType
from .rotation import QuantizedRotation, QuantizedRotationType


class XOperator(QOperatorBase, QuantizedRotation):
    """Creates an XOperator class with XOperator .

    :param QOperatorBase: [description]
    :type QOperatorBase: [type]
    :param QuantizedRotation: [description]
    :type QuantizedRotation: [type]
    """

    def __init__(
        self,
        target_qubit_index: int,
    ) -> None:
        QOperatorBase.__init__(self, QOperatorType.X, target_qubit_index)
        QuantizedRotation.__init__(self, QuantizedRotationType.SWAP)

    def __call__(self, qstate: QState) -> Any:
        """
        This method is used to apply a quantum gate operation to a quantum state.
        @param qstate - The input quantum state.
        @return The modified quantum state after applying the gate operation.
        """
        return qstate.apply_x(self.target_qubit_index)

    def __str__(self) -> str:
        """The repr of the class .

        :return: [description]
        :rtype: str
        """

        return f"X({self.target_qubit_index})"

    def get_cost(self) -> int:
        """Returns the cost of the job .

        :return: [description]
        :rtype: int
        """
        return 0
