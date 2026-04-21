"""Mapping of multi-controlled rotation gates to primitive sequences."""

from __future__ import annotations

from collections import namedtuple
from typing import List

import numpy as np

from xyz.decomposition.gray_code import (
    control_sequence_to_gates,
    decompose_mcry,
)
from xyz.gates.types import QGateType


def theta_to_unitary(theta: float):
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


def map_muxy(gate) -> list:
    assert gate.qgate_type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubits[0]], gate.target_qubit
    )
    return gates


def map_mcry(gate) -> list:
    match gate.qgate_type:
        case QGateType.MCRY:
            control_qubits = gate.control_qubits
            phases = gate.phases
            target_qubit = gate.target_qubit
        case QGateType.CRY:
            control_qubits = list(gate.control_qubits)
            phases = [gate.phase]
            target_qubit = gate.target_qubit
        case _:
            raise ValueError("Not a MCRY gate")
    rotation_table = np.zeros(2 ** (len(control_qubits)))
    rotated_index = 0
    for i, controlled_by_one in enumerate(phases):
        if controlled_by_one is True:
            rotated_index += 2**i

    rotation_table[rotated_index] = gate.theta
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(control_sequence, control_qubits, target_qubit)
    return gates


def map_mcmy(gate) -> list:
    rotation_table = gate.rotation_table
    control_sequence = decompose_mcry(rotation_table=rotation_table)
    gates = control_sequence_to_gates(
        control_sequence,
        gate.control_qubits,
        gate.target_qubit,
    )
    return gates


def map_mcry_linear(mcry_gate) -> list:
    from xyz.gates.controlled import CRX, CU
    from xyz.gates.single import X

    assert mcry_gate.qgate_type == QGateType.MCRY

    qubit_list = list(mcry_gate.control_qubits) + [mcry_gate.target_qubit]
    num_qubits = len(qubit_list)

    if num_qubits == 1:
        from xyz.gates.single import RY
        return [RY(mcry_gate.theta, qubit_list[0])]

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
        gates: list = []
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

    unitary = theta_to_unitary(mcry_gate.theta)

    gates: list = []
    for phase, control_qubit in zip(mcry_gate.phases, mcry_gate.control_qubits):
        if phase == 0:
            gates.append(X(control_qubit))

    gates_c1 = convert_rec(unitary, num_qubits)
    gates_c2 = convert_rec(unitary, num_qubits, step=-1)
    gates_c3 = convert_rec(unitary, num_qubits - 1, is_first=False)
    gates_c4 = convert_rec(unitary, num_qubits - 1, is_first=False, step=-1)

    gates.extend(gates_c1)
    gates.extend(gates_c2)
    gates.extend(gates_c3)
    gates.extend(gates_c4)

    for phase, control_qubit in zip(mcry_gate.phases, mcry_gate.control_qubits):
        if phase == 0:
            gates.append(X(control_qubit))
    return gates
