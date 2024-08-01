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
    """Classmethod for creating a controlled gate ."""

    def __init__(self, control_qubit: QBit, phase: int = 1) -> None:
        self.phase = phase

        assert isinstance(control_qubit, QBit)
        self.control_qubit = control_qubit

    def get_control_qubit(self) -> QBit:
        """Returns the control qubit ."""
        return self.control_qubit

    def get_phase(self) -> int:
        """Returns the phase ."""
        return self.phase

    def is_enabled(self, index: int):
        """Returns True if the control qubit is enabled ."""
        return (index >> self.control_qubit.index) & 1 == self.phase


class MultiControlledGate:
    """Class method for creating a multiControlledGate ."""

    def __init__(self, control_qubits: List[QBit], phases: List[int]) -> None:
        self.control_qubits = control_qubits[:]
        self.phases = list(phases)[:]

    def has_zero_controls(self) -> bool:
        """Returns True if any control qubits are zero ."""
        return len(self.control_qubits) == 0

    def has_one_control(self) -> bool:
        """Returns True if this instruction has one control ."""
        return len(self.control_qubits) == 1

    def get_control_qubits(self) -> List[QBit]:
        """Returns the control qubits ."""
        return self.control_qubits

    def get_phases(self) -> List[int]:
        """Returns the phases ."""
        return self.phases

    def is_enabled(self, index: int) -> bool:
        """Returns True if the control qubits are enabled ."""
        for control_qubit, phase in zip(self.control_qubits, self.phases):
            if (index >> control_qubit.index) & 1 != phase:
                return False
        return True
