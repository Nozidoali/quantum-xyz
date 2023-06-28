#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:36:46
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:42:30
"""

from typing import Any
from .QOperatorBase import *
from .QuantizedRotation import *
from .QState import *


class XOperator(QOperatorBase, QuantizedRotation):
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
        new_states = QState([], qstate.num_qubits)

        pure_state: PureState

        for pure_state in qstate():
            new_states.add_pure_state(pure_state.flip(self.target_qubit_index))

        return new_states
