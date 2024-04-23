#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:31:33
"""

from typing import List
import numpy as np

from .qstate import QState
from .base import BasicGate, MultiControlledGate, QBit, QGateType, RotationGate

MCRY_CNOT_COST = {
    "0": 0,
    "1": 2,
    "2": 4,
    "3": 8,
    "4": 16,
    "5": 32,
    "6": 64,
    "7": 128,
    "8": 226,
    "9": 290,
    "10": 362,
    "11": 442,
    "12": 530,
    "13": 626,
    "14": 730,
    "15": 842,
    "16": 962,
    "17": 1090,
    "18": 1226,
    "19": 1370,
    "20": 1522,
    "21": 1682,
    "22": 1850,
    "23": 2026,
    "24": 2210,
    "25": 2402,
    "26": 2602,
    "27": 2810,
    "28": 3026,
}


class MCRY(RotationGate, BasicGate, MultiControlledGate):
    """Classmethod to create a multi-controlled  gate .

    :param RotationGate: [description]
    :type RotationGate: [type]
    :param BasicGate: [description]
    :type BasicGate: [type]
    :param MultiControlledGate: [description]
    :type MultiControlledGate: [type]
    """

    def __init__(
        self,
        theta: float,
        control_qubits: List[QBit],
        phases: List[int],
        target_qubit: QBit,
    ) -> None:
        BasicGate.__init__(self, QGateType.MCRY, target_qubit)
        RotationGate.__init__(self, theta)
        MultiControlledGate.__init__(self, control_qubits, phases)

    def __str__(self) -> str:
        control_str = "+".join(
            [
                str(qubit) + f"[{phase}]"
                for qubit, phase in zip(self.control_qubits, self.phases)
            ]
        )
        return f"MCRY({self.target_qubit.index}:{self.theta:0.02f}, {control_str})"

    def get_cnot_cost(self) -> int:
        """Returns the cost of the cost of the gate."""
        index_str = str(len(self.control_qubits))
        if index_str not in MCRY_CNOT_COST:
            raise ValueError(
                f"len(self.control_qubits) = {len(self.control_qubits)} is not supported"
            )
        return MCRY_CNOT_COST[index_str]

    def conjugate(self) -> "MCRY":
        """Conjugate the gate ."""
        return MCRY(-self.theta, self.control_qubits, self.phases, self.target_qubit)

    def apply(self, qstate: QState) -> QState:
        """Apply the gate to the state."""
        index_to_weight = {idx: 0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            # no rotation
            if not self.is_enabled(idx):
                index_to_weight[idx] = qstate.index_to_weight[idx]
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0

            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] += weight * np.sin(self.theta / 2)
            else:
                index_to_weight[idx] += weight * np.cos(self.theta / 2)
                index_to_weight[rdx] -= weight * np.sin(self.theta / 2)
        return QState(index_to_weight, qstate.num_qubits)
