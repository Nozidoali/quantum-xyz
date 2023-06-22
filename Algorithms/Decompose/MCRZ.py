#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 15:58:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 21:47:46
"""

import numpy as np
from Utils import *
from Circuit import *

def apply_control_sequence_to_z(
    circuit: QCircuit, control_sequence: list, control_qubits: list, target_qubit
) -> None:
    for control in control_sequence:
        rotation_theta, control_id = control

        circuit.rz(rotation_theta, target_qubit)
        circuit.cx(control_qubits[control_id], target_qubit)


def decompose_multiple_controlled_rotation_Z_gate(
    matrix: np.ndarray, circuit: QCircuit, control_qubits: list, target_qubit
):

    num_qubits = len(control_qubits)

    alphas = -2 * np.imag(np.log(matrix.diagonal()))

    control_sequence = synthesize_multi_controlled_rotations(alphas)
    apply_control_sequence_to_z(circuit, control_sequence, control_qubits, target_qubit)