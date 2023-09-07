#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 22:43:37
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 00:14:40
"""

from typing import List
import numpy as np

from .basic_gates import QGate, QGateType, MULTIPLEXY
from .decomposition import decompose_mcry, control_sequence_to_gates


def __map_muxy(gate: MULTIPLEXY) -> List[QGate]:
    """Convert a multi - gate into a list of gates .

    :param gate: [description]
    :type gate: MULTIPLEXY
    :return: [description]
    :rtype: List[QGate]
    """
    assert gate.type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]

    control_sequence = decompose_mcry(rotation_table)

    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubit], gate.target_qubit
    )

    return gates


def __map_mcry(gate: QGate) -> List[QGate]:
    """Convert a MCRY gate into a list of gates .

    :param gate: [description]
    :type gate: QGate
    :raises Exception: [description]
    :return: [description]
    :rtype: List[QGate]
    """
    match gate.get_qgate_type():
        case QGateType.MCRY:
            control_qubits = gate.control_qubits
            phases = gate.phases
            target_qubit = gate.target_qubit

        case QGateType.CRY:
            control_qubits = [gate.control_qubit]
            phases = [gate.phase]
            target_qubit = gate.target_qubit

        case _:
            raise ValueError("Not a MCRY gate")

    # we prepare the rotation table
    rotation_table = np.zeros(2 ** (len(control_qubits)))

    rotated_index = 0
    for i, controlled_by_one in enumerate(phases):
        if controlled_by_one is True:
            rotated_index += 2**i

    # only rotate the target qubit if the control qubits are in the positive phase
    rotation_table[rotated_index] = gate.theta

    control_sequence = decompose_mcry(rotation_table)

    gates = control_sequence_to_gates(control_sequence, control_qubits, target_qubit)

    return gates


def add_gate_mapped(self, gate: QGate) -> None:
    """Add a gate to the circuit .

    :param gate: [description]
    :type gate: QGate
    """
    if not self.map_gates:
        self.append_gate(gate)
        return

    match gate.qgate_type:
        case QGateType.MULTIPLEX_Y:
            gates = __map_muxy(gate)
            self.append_gates(gates)

        case QGateType.MCRY:
            gates = __map_mcry(gate)
            self.append_gates(gates)

        case QGateType.CRY:
            gates = __map_mcry(gate)
            self.append_gates(gates)

        case _:
            self.append_gate(gate)
