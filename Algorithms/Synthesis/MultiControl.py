#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-19 19:20:10
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 20:54:16
'''

from Circuit import *
from Utils import *
from .GrayCode import *

import numpy as np

def synthesize_multi_controlled_rotations(rotation_table: list):
    
    num_controls = int(np.log2(len(rotation_table)))
    
    alphas = rotation_table[:]
    thetas = find_thetas(alphas)
    
    # return a list of control sequences
    control_sequence: list = []

    for i, theta in enumerate(thetas):

        # get the number of gray code
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 2, 1, 2, 3, 2, 1, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        control_id = bin(i ^ (i >> 1)).count("1") - 1

        # CNOT
        if control_id >= 0:

            assert control_id < num_controls
            control_sequence.append((control_id, theta))

        else:
            control_sequence.append((None, theta))

    control_sequence.append((num_controls - 1, 0))
    
    return control_sequence