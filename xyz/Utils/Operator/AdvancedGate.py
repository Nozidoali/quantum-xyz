#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-19 11:52:54
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 21:36:05
"""

import numpy as np
from .BasicGate import *


class AdvancedGate:
    def mcry(theta, control_qubits: dict, target_index, num_qubits: int):
        c1 = np.array([[1, 0], [0, 0]])
        c2 = np.array([[0, 0], [0, 1]])

        ry: np.ndarray = BasicGate.ry(theta)
        ry00 = ry[0, 0]
        ry01 = ry[0, 1]
        ry10 = ry[1, 0]
        ry11 = ry[1, 1]

        matrix = np.zeros((2**num_qubits, 2**num_qubits))

        for j in range(2**num_qubits):
            control_state = True

            target_val = (j >> target_index) & 1
            if target_val == 0:
                continue

            j_inv = j ^ (1 << target_index)

            for q in control_qubits:
                q_val = (j >> q) & 1

                controlled_by_one = control_qubits[q]

                # if the control qubit is in the wrong state
                if (controlled_by_one and q_val == 0) or (
                    not controlled_by_one and q_val == 1
                ):
                    control_state = False
                    break

            # we get the control states
            if not control_state:
                matrix[j, j] = 1
                matrix[j_inv, j_inv] = 1
                continue

            else:
                matrix[j, j] = ry00
                matrix[j, j_inv] = ry10
                matrix[j_inv, j] = ry01
                matrix[j_inv, j_inv] = ry11

        return matrix
