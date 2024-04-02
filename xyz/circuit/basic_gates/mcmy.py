#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-16 15:01:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-16 15:04:34
"""

from typing import List

from .base import AdvancedGate, QBit, QGateType


class MCMY(AdvancedGate):
    """Returns a multi-controlled mux Y class .

    :param AdvancedGate: [description]
    :type AdvancedGate: [type]
    """

    def __init__(
        self,
        rotation_table: List[float],
        control_qubits: List[QBit],
        target_qubit: QBit,
    ) -> None:
        AdvancedGate.__init__(self, QGateType.MCMY)

        assert isinstance(target_qubit, QBit)
        assert isinstance(control_qubits, list)

        self.target_qubit: QBit = target_qubit
        self.control_qubits: QBit = control_qubits
        self.rotation_table: List[float] = rotation_table

    def __str__(self) -> str:
        control_qubit_str = ",".join([str(qubit) for qubit in self.control_qubits])
        return f"MCMY({control_qubit_str})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate.

        :return: [description]
        :rtype: int
        """
        return 1 << len(self.control_qubits)

    def apply(self, qstate: "QState") -> "QState":
        raise NotImplementedError("MCMY gate is not implemented yet")
