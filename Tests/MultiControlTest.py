#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-19 21:22:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 21:27:44
"""

from Algorithms import *
from xyz.Utils import *


def test_multi_control():
    matrix = AdvancedGate.mcry(
        theta=np.pi, control_qubits={0: False, 1: False}, target_index=2, num_qubits=3
    )

    control_sequence = synthesize_multi_controlled_rotations(
        rotation_table=[np.pi, 0, 0, 0]
    )

    print(matrix)
    print(control_sequence)
