#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-20 00:05:16
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-20 00:06:35
"""

import numpy as np


def D_state(num_qubits: int, num_bits: int) -> np.ndarray:
    """dicke state.
    """
    state = np.zeros(2**num_qubits)

    ones: float = 0

    for i in range(2**num_qubits):
        num_ones = bin(i).count("1")
        if num_ones == num_bits:
            state[i] = 1
            ones += 1

    return 1 / np.sqrt(ones) * state
