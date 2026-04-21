"""Gray-code based decomposition of multi-controlled rotations into
single-qubit rotations and CNOTs."""

from __future__ import annotations

from typing import List

import numpy as np
import scipy as sp


def find_thetas(alphas):
    size = len(alphas)
    gray_code_coefficient_matrix = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            bitwise_inner_product = bin(i & (j ^ (j >> 1))).count("1")
            gray_code_coefficient_matrix[i, j] = (-1) ** bitwise_inner_product
    thetas = sp.linalg.solve(gray_code_coefficient_matrix, alphas)
    return thetas


def decompose_mcry(rotation_table: list):
    num_controls = int(np.log2(len(rotation_table)))
    assert num_controls > 0, "The number of controls must be greater than 0"

    alphas = rotation_table[:]
    thetas = find_thetas(alphas)

    control_sequence: list = []
    prev_gray_code = 0

    for i, theta in enumerate(thetas):
        curr_gray_code = ((i + 1) ^ ((i + 1) >> 1)) if i < (2**num_controls) - 1 else 0
        diff = curr_gray_code ^ prev_gray_code
        prev_gray_code = curr_gray_code
        control_id = int(np.log2(diff))
        control_sequence.append((theta, control_id))

    return control_sequence


def control_sequence_to_gates(
    control_sequence: list, control_qubits: list, target_qubit
) -> list:
    from xyz.gates.controlled import CX
    from xyz.gates.single import RY

    gates: list = []
    for control in control_sequence:
        rotation_theta, control_id = control
        gates.append(RY(rotation_theta, target_qubit))
        gates.append(CX(control_qubits[control_id], 1, target_qubit))
    return gates
