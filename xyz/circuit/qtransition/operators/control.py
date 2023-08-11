#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:27:44
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:29:03
"""

from typing import List
from .qstate import PureState


class ControlledOperator:
    """Class method for creating the ControlledOperator ."""

    def __init__(self, control_qubit_index: int, control_qubit_phase: bool) -> None:
        self.control_qubit_index: int = control_qubit_index
        self.control_qubit_phase: bool = control_qubit_phase


class MultiControlledOperator:
    """Class method to create a class that is used by the FirmrolledOperator ."""

    def __init__(
        self, control_qubit_indices: List[int], control_qubit_phases: List[bool]
    ) -> None:
        self.control_qubit_indices = control_qubit_indices
        self.control_qubit_phases = control_qubit_phases

    def is_controlled(self, pure_state: PureState) -> bool:
        """Returns True if the pure_state is controlled by the gate .

        :param pure_state: [description]
        :type pure_state: PureState
        :return: [description]
        :rtype: bool
        """
        for index, phase in zip(self.control_qubit_indices, self.control_qubit_phases):
            if (int(pure_state) >> index) & 1 != phase:
                return False

        return True
