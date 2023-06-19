#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 15:58:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 21:47:54
"""

import numpy as np
from ..Synthesis import *


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
    thetas = find_thetas(alphas)

    assert num_qubits == np.log2(len(thetas))

    for i, theta in enumerate(thetas):

        # get the number of gray code
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i >> 1)).count("1") - 1

        # CNOT
        if control_id >= 0:

            assert control_id < num_qubits
            circuit.cx(control_qubits[control_id], target_qubit)

        # rotate the target qubit
        circuit.ry(theta, target_qubit)
    
    control_qubit = control_qubits[-1]
    circuit.cx(control_qubit, target_qubit)
