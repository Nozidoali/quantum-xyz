#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:27:44
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:29:03
"""

from typing import List


class ControlledOperator:
    """Class method for creating the ControlledOperator ."""

    def __init__(self, control_qubit_index: int, control_qubit_phase: bool) -> None:
        self.control_qubit_index: int = control_qubit_index
        self.control_qubit_phase: bool = control_qubit_phase

    def is_controlled(self, basis_state: int) -> bool:
        """Returns whether the basis state is controlled by the basis state .

        :param basis_state: [description]
        :type basis_state: int
        :return: [description]
        :rtype: bool
        """
        return (basis_state >> self.control_qubit_index) & 1 == self.control_qubit_phase


class MultiControlledOperator:
    """Class method to create a class that is used by the FirmrolledOperator ."""

    def __init__(
        self, control_qubit_indices: List[int], control_qubit_phases: List[bool]
    ) -> None:
        self.control_qubit_indices = control_qubit_indices
        self.control_qubit_phases = control_qubit_phases

    def is_controlled(self, basis_state: int) -> bool:
        """Returns whether the basis state is controlled by the basis state .

        :param basis_state: [description]
        :type basis_state: int
        :return: [description]
        :rtype: bool
        """
        for i, control_qubit in enumerate(self.control_qubit_indices):
            if (basis_state >> control_qubit) & 1 != self.control_qubit_phases[i]:
                return False
        return True
