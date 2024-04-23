#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 12:44:45
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 12:46:16
"""

from typing import List
import numpy as np

from scipy.linalg import solve

from xyz.utils import call_with_global_timer
from ..gate import QGate, RY, CX, QBit


@call_with_global_timer
def find_thetas(alphas):
    """Find theta matrix for the given alphas .

    :param alphas: [description]
    :type alphas: [type]
    :return: [description]
    :rtype: [type]
    """
    size = len(alphas)
    # for the gray code matrix
    gray_code_coefficient_matrix = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            #  The exponent is the bit-wise inner product of the binary vectors for the standard binary code representation of the integer i (bi) and the binary representation of the i th value of the gray code up to a value of 2) The j th value of the gray code is calculated using the bit-wise XOR of the unsigned binary j and a single shift right of the value of j , like so: ”j XOR (j>>1)” for C++ code

            bitwise_inner_product = bin(i & (j ^ (j >> 1))).count("1")
            gray_code_coefficient_matrix[i, j] = (-1) ** bitwise_inner_product

    thetas = solve(gray_code_coefficient_matrix, alphas)

    return thetas


@call_with_global_timer
def decompose_mcry(rotation_table: list):
    """Synthesize multiple controlled rotations .

    :param rotation_table: [description]
    :type rotation_table: list
    :return: [description]
    :rtype: [type]
    """
    num_controls = int(np.log2(len(rotation_table)))

    assert num_controls > 0, "The number of controls must be greater than 0"

    alphas = rotation_table[:]
    thetas = find_thetas(alphas)

    # return a list of control sequences
    control_sequence: list = []

    prev_gray_code = 0

    # print(f"num_controls: {num_controls}, thetas: {thetas}")

    for i, theta in enumerate(thetas):
        # get the bit that changed in the i of gray code
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 0, 2, 0, 1, 0, 2, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        curr_gray_code = (
            ((i + 1) ^ ((i + 1) >> 1)) if i < (2**num_controls) - 1 else 0
        )

        diff = curr_gray_code ^ prev_gray_code
        # print(f"i: {i}, curr_gray_code: {curr_gray_code}, prev_gray_code: {prev_gray_code}, diff: {diff}")
        prev_gray_code = curr_gray_code

        control_id = int(np.log2(diff))

        control_sequence.append((theta, control_id))

    return control_sequence


@call_with_global_timer
def control_sequence_to_gates(
    control_sequence: list, control_qubits: List[QBit], target_qubit: QBit
) -> List[QGate]:
    """Convert a control sequence into a list of gates .

    :param control_sequence: [description]
    :type control_sequence: list
    :param control_qubits: [description]
    :type control_qubits: List[QBit]
    :param target_qubit: [description]
    :type target_qubit: QBit
    :return: [description]
    :rtype: List[QGate]
    """
    gates: List[QGate] = []

    for control in control_sequence:
        rotation_theta, control_id = control

        gates.append(RY(rotation_theta, target_qubit))
        gates.append(CX(control_qubits[control_id], 1, target_qubit))

    return gates
