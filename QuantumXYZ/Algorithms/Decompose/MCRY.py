#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 15:58:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 21:47:54
"""

import numpy as np
from Utils import *
from Circuit import *


def apply_control_sequence_to_y(
    circuit: QCircuit, control_sequence: list, control_qubits: list, target_qubit
) -> None:
    for control in control_sequence:
        rotation_theta, control_id = control

        circuit.ry(rotation_theta, target_qubit)
        circuit.cx(control_qubits[control_id], target_qubit)


def decompose_multiple_controlled_rotation_Y_gate(
    matrix: np.ndarray, circuit, control_qubits: list, target_qubit
):
    num_qubits = len(control_qubits)

    if num_qubits == 0:
        assert target_qubit is not None

        # this is a special case, in this case, we simply apply an RY gate to the target qubit
        circuit.ry(2 * np.arcsin(matrix[0, 0]), target_qubit)
        return

    alphas = 2 * np.arcsin(matrix.diagonal())

    control_sequence = synthesize_multi_controlled_rotations(alphas)
    apply_control_sequence_to_y(circuit, control_sequence, control_qubits, target_qubit)
