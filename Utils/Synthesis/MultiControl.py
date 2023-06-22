#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-19 19:20:10
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 20:54:16
"""

from .GrayCode import *

import numpy as np


def synthesize_multi_controlled_rotations(rotation_table: list):

    num_controls = int(np.log2(len(rotation_table)))

    alphas = rotation_table[:]
    thetas = find_thetas(alphas)

    # return a list of control sequences
    control_sequence: list = []

    prev_gray_code = 0

    for i, theta in enumerate(thetas):

        # get the bit that changed in the i of gray code
        # for example, if num_qubits = 3, then the gray code is 000, 001, 011, 010, 110, 111, 101, 100
        # the control id is 0, 1, 0, 2, 0, 1, 0, 2, respectively
        # which is determined by the number of 1 in the binary representation of the gray code
        curr_gray_code = ((i+1) ^ ((i+1) >> 1)) if i < (2 ** num_controls) - 1 else 0

        diff = curr_gray_code ^ prev_gray_code
        # print(f"i: {i}, curr_gray_code: {curr_gray_code}, prev_gray_code: {prev_gray_code}, diff: {diff}")
        prev_gray_code = curr_gray_code

        control_id = int(np.log2(diff))

        control_sequence.append((theta, control_id))

    return control_sequence
