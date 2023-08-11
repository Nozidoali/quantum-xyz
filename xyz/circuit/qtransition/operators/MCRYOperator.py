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
from .MultiControlledOperator import *
from .qstate import *


class MCRYOperator(QOperatorBase, QuantizedRotation, MultiControlledOperator):
    def __init__(
        self,
        target_qubit_index: int,
        rotation_type: QuantizedRotationType,
        control_qubit_indices: List[int],
        control_qubit_phases: List[bool],
    ) -> None:
        QOperatorBase.__init__(self, QOperatorType.MCRY, target_qubit_index)
        QuantizedRotation.__init__(self, rotation_type)
        MultiControlledOperator.__init__(
            self, control_qubit_indices, control_qubit_phases
        )

    def __call__(self, qstate: QState) -> Any:
        """
        This method is used to apply a quantum gate operation to a quantum state.
        @param qstate - The input quantum state.
        @return The modified quantum state after applying the gate operation.
        """
        new_states = QState([], qstate.num_qubits)

        pure_state: PureState

        for pure_state in qstate():
            # check the unateness
            if not self.is_controlled(pure_state):
                new_states.add_pure_state(pure_state)
                continue

            match self.rotation_type:
                case QuantizedRotationType.SWAP:
                    new_states.add_pure_state(pure_state.flip(self.target_qubit_index))

                case QuantizedRotationType.MERGE0:
                    if pure_state.flip(self.target_qubit_index) not in qstate:
                        raise ValueError("The target state is not in the qstate")

                    new_states.add_pure_state(pure_state.set0(self.target_qubit_index))

                case QuantizedRotationType.MERGE1:
                    if pure_state.flip(self.target_qubit_index) not in qstate:
                        raise ValueError("The target state is not in the qstate")

                    new_states.add_pure_state(pure_state.set1(self.target_qubit_index))

        return new_states

    def get_cost(self) -> int:
        num_controls: int = len(self.control_qubit_indices)
        if num_controls == 0:
            return 0
        elif num_controls == 1 and self.rotation_type == QuantizedRotationType.SWAP:
            return 1
        else:
            return 1 << (num_controls)

    def __str__(self) -> str:
        rotation_str = (
            "X"
            if self.rotation_type is QuantizedRotationType.SWAP
            else "Y"
            if self.rotation_type is QuantizedRotationType.MERGE0
            else "Y"
        )
        return f"MCRY({self.target_qubit_index}, {rotation_str}, {self.control_qubit_indices}, {self.control_qubit_phases})"

    def __invert__(self):
        match self.rotation_type:
            case QuantizedRotationType.SWAP:
                self.rotation_type = QuantizedRotationType.SWAP

            case QuantizedRotationType.MERGE0:
                self.rotation_type = QuantizedRotationType.SPLIT0

            case QuantizedRotationType.MERGE1:
                self.rotation_type = QuantizedRotationType.SPLIT1

            case QuantizedRotationType.SPLIT0:
                self.rotation_type = QuantizedRotationType.MERGE0

            case QuantizedRotationType.SPLIT1:
                self.rotation_type = QuantizedRotationType.MERGE1

        return self
