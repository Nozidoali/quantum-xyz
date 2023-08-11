#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:09:23
"""

from typing import List

from .qubit import QBit

class ControlledGate:
    """Classmethod for creating a controlled gate .
    """
    def __init__(self, control_qubit: QBit, phase: int = 1) -> None:
        self.phase = phase

        assert isinstance(control_qubit, QBit)
        self.control_qubit = control_qubit

class MultiControlledGate:
    """Class method for creating a multiControlledGate .
    """
    def __init__(self, control_qubits: List[QBit], phases: List[int]) -> None:
        self.control_qubits = control_qubits
        self.phases = phases

    def has_zero_controls(self) -> bool:
        """Returns True if any control qubits are zero .

        :return: [description]
        :rtype: bool
        """
        return len(self.control_qubits) == 0

    def has_one_control(self) -> bool:
        """Returns True if this instruction has one control .

        :return: [description]
        :rtype: bool
        """
        return len(self.control_qubits) == 1
