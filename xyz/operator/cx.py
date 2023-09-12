#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-27 00:10:55
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-27 00:41:20
"""

from typing import Any

from xyz.qstate import QState

from .operator import QOperatorBase, QOperatorType
from .rotation import QuantizedRotation, QuantizedRotationType
from .control import ControlledOperator


class CXOperator(QOperatorBase, QuantizedRotation, ControlledOperator):
    """Creates an CXOperator class with CXOperator .

    :param QOperatorBase: [description]
    :type QOperatorBase: [type]
    :param QuantizedRotation: [description]
    :type QuantizedRotation: [type]
    """

    def __init__(
        self,
        target_qubit_index: int,
        control_qubit_index: int,
        control_qubit_phase: bool,
    ) -> None:
        QOperatorBase.__init__(self, QOperatorType.CX, target_qubit_index)
        QuantizedRotation.__init__(self, QuantizedRotationType.SWAP)
        ControlledOperator.__init__(self, control_qubit_index, control_qubit_phase)

    def __call__(self, qstate: QState) -> Any:
        """
        This method is used to apply a quantum gate operation to a quantum state.
        @param qstate - The input quantum state.
        @return The modified quantum state after applying the gate operation.
        """
        return qstate.apply_cx(
            self.control_qubit_index, self.control_qubit_phase, self.target_qubit_index
        )

    def __str__(self) -> str:
        """The repr of the class .

        :return: [description]
        :rtype: str
        """
        phase_str = "~" if self.control_qubit_phase else ""

        return f"C({phase_str}{self.control_qubit_index})X({self.target_qubit_index})"

    def get_cost(self) -> int:
        """Returns the cost of the job .

        :return: [description]
        :rtype: int
        """
        return 1
