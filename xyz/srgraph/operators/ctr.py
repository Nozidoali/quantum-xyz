#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-27 00:21:52
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-27 01:10:43
"""

from typing import Any

from .qstate import QState
from .operator import QOperatorBase, QOperatorType
from .rotation import QuantizedRotation, QuantizedRotationType
from .control import ControlledOperator


class CTROperator(QOperatorBase, QuantizedRotation, ControlledOperator):
    """Creates an CXOperator class with CXOperator .

    :param QOperatorBase: [description]
    :type QOperatorBase: [type]
    :param QuantizedRotation: [description]
    :type QuantizedRotation: [type]
    """

    def __init__(
        self,
        target_qubit_index: int,
        target_phase: bool,
        control_qubit_index: int,
        control_qubit_phase: bool,
    ) -> None:
        if target_phase is True:
            QOperatorBase.__init__(self, QOperatorType.CT1, target_qubit_index)
            QuantizedRotation.__init__(self, QuantizedRotationType.MERGE1)
            ControlledOperator.__init__(self, control_qubit_index, control_qubit_phase)
        else:
            QOperatorBase.__init__(self, QOperatorType.CT0, target_qubit_index)
            QuantizedRotation.__init__(self, QuantizedRotationType.MERGE0)
            ControlledOperator.__init__(self, control_qubit_index, control_qubit_phase)

        # The angle of the rotation.
        self.theta = None

    def __call__(self, qstate: QState) -> Any:
        """
        This method is used to apply a quantum gate operation to a quantum state.
        @param qstate - The input quantum state.
        @return The modified quantum state after applying the gate operation.
        """
        try:
            if self.operator_type == QOperatorType.CT0:
                next_state, theta = qstate.apply_controlled_merge0(
                    self.control_qubit_index,
                    self.control_qubit_phase,
                    self.target_qubit_index,
                )
                self.theta = theta
                return next_state

            if self.operator_type == QOperatorType.CT1:
                next_state, theta = qstate.apply_controlled_merge1(
                    self.control_qubit_index,
                    self.control_qubit_phase,
                    self.target_qubit_index,
                )
                self.theta = theta
                return next_state
        except ValueError:
            raise ValueError("The target qubit is not in the state.")

    def __str__(self) -> str:
        """The repr of the class .

        :return: [description]
        :rtype: str
        """
        phase_str = "~" if self.control_qubit_phase else ""
        target_phase_str = "1" if self.operator_type == QOperatorType.CT1 else "0"

        return f"C({phase_str}{self.control_qubit_index})TR({self.target_qubit_index}->{target_phase_str})"

    def get_cost(self) -> int:
        """Returns the cost of the job .

        :return: [description]
        :rtype: int
        """
        return 2
