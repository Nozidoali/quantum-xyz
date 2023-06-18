#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 15:58:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 17:38:02
'''

import numpy as np
from .BGMatrix import *

def decompose_multiple_controlled_rotation_Z_gate(matrix: np.ndarray, circuit, control_qubits: list, target_qubit):

    num_qubits = len(control_qubits)
    
    alphas = -2 * np.imag( np.log( matrix.diagonal() ) )
    thetas = find_thetas(alphas)

    assert num_qubits == np.log2(len(thetas))

    for i, theta in enumerate(thetas):

        # get the number of gray code 
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i>>1)).count('1') - 1

        # CNOT
        if control_id >= 0:
            
            assert control_id < num_qubits
            circuit.cnot(control_qubits[control_id], target_qubit)

        # rotate the target qubit
        circuit.rz(theta, target_qubit)

    control_id = num_qubits - 1 # reset the control id
    circuit.cnot(control_qubits[control_id], target_qubit)