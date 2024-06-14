#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 22:43:37
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 00:14:40
"""

from collections import namedtuple

from typing import List
import numpy as np

from xyz.circuit.gate.ry import RY
from xyz.utils import call_with_global_timer

from .gate import QGate, QGateType, MULTIPLEXY, CRX, CU, MCRY, X, MCMY
from .decomposition import decompose_mcry, control_sequence_to_gates


def __map_muxy(gate: MULTIPLEXY) -> List[QGate]:
    assert gate.type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]

    control_sequence = decompose_mcry(rotation_table)

    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubit], gate.target_qubit
    )

    return gates


def __map_mcry(gate: QGate) -> List[QGate]:
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


def __map_mcmy(gate: MCMY) -> List[QGate]:
    """Convert a MCMY gate into a list of gates ."""

    rotation_table = gate.rotation_table
    control_sequence = decompose_mcry(rotation_table=rotation_table)

    gates = control_sequence_to_gates(
        control_sequence,
        gate.control_qubits,
        gate.target_qubit,
    )

    return gates


def theta_to_unitary(theta: float):
    """Converts theta to a unitary unitary gate ."""
    raw_matrix = np.array(
        [
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )
    return raw_matrix


def unitary_convert(unitary: np.ndarray, coef: float, signal: int):
    param = 1 / np.abs(coef)

    values, vectors = np.linalg.eig(unitary)
    updated_unitary = (
        np.power(values[0] + 0j, param) * vectors[:, [0]] @ vectors[:, [0]].conj().T
    )
    updated_unitary = (
        updated_unitary
        + np.power(values[1] + 0j, param) * vectors[:, [1]] @ vectors[:, [1]].conj().T
    )

    if signal < 0:
        updated_unitary = np.linalg.inv(updated_unitary)

    return updated_unitary


def __map_mcry_linear(mcry_gate: MCRY) -> List[QGate]:
    assert mcry_gate.get_qgate_type() == QGateType.MCRY

    # we first preprocess the relavant qubits
    qubit_list = mcry_gate.control_qubits + [mcry_gate.target_qubit]
    num_qubits = len(qubit_list)

    # special case for single qubit
    if num_qubits == 1:
        gates = []
        gate = RY(mcry_gate.theta, qubit_list[0])
        gates.append(gate)
        return gates

    # special case for two qubits
    # if num_qubits == 2:
    #     gates = __map_mcry(mcry_gate)
    #     return gates

    # now we handle the general case
    def convert_rec(
        unitary: np.ndarray, num_qubits: int, is_first: bool = True, step: int = 1
    ):
        nonlocal qubit_list

        pairs = namedtuple("pairs", ["control", "target"])

        if step == 1:
            start = 0
            reverse = True

        else:
            start = 1
            reverse = False

        qubit_pairs = [
            pairs(control, target)
            for target in range(num_qubits)
            for control in range(start, target)
        ]

        qubit_pairs.sort(key=lambda e: e.control + e.target, reverse=reverse)

        gates = []
        for pair in qubit_pairs:
            exponent = pair.target - pair.control
            if pair.control == 0:
                exponent = exponent - 1
            param = 2**exponent
            signal = -1 if (pair.control == 0 and not is_first) else 1
            signal = signal * step

            if pair.target == num_qubits - 1 and is_first:
                updated_unitary = unitary_convert(unitary, param, signal)
                gate = CU(
                    updated_unitary,
                    qubit_list[pair.control],
                    True,
                    qubit_list[pair.target],
                )
                gates.append(gate)
            else:
                gate = CRX(
                    signal * np.pi / param,
                    qubit_list[pair.control],
                    True,
                    qubit_list[pair.target],
                )
                gates.append(gate)

        return gates

    unitary = theta_to_unitary(mcry_gate.get_theta())

    gates = []
    # frist we consider the control phases
    for phase, control_qubit in zip(mcry_gate.get_phases(), mcry_gate.control_qubits):
        if phase == 0:
            gate = X(control_qubit)
            gates.append(gate)

    gates_c1 = convert_rec(unitary, num_qubits)
    gates_c2 = convert_rec(unitary, num_qubits, step=-1)
    gates_c3 = convert_rec(unitary, num_qubits - 1, is_first=False)
    gates_c4 = convert_rec(unitary, num_qubits - 1, is_first=False, step=-1)

    for gate in gates_c1:
        gates.append(gate)
    for gate in gates_c2:
        gates.append(gate)
    for gate in gates_c3:
        gates.append(gate)
    for gate in gates_c4:
        gates.append(gate)

    # frist we consider the control phases
    for phase, control_qubit in zip(mcry_gate.get_phases(), mcry_gate.control_qubits):
        if phase == 0:
            gate = X(control_qubit)
            gates.append(gate)

    return gates


@call_with_global_timer
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
            if len(gate.get_control_qubits()) >= 8:
                gates = __map_mcry_linear(gate)
            else:
                gates = __map_mcry(gate)

            # this may cause problem if the gates returned are still MCRYs
            self.add_gates(gates)

        case QGateType.MCMY:
            gates = __map_mcmy(gate)

            self.add_gates(gates)

        case QGateType.CRY:
            gates = __map_mcry(gate)
            self.append_gates(gates)

        case _:
            self.append_gate(gate)
