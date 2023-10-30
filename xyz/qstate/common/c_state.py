#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-20 00:05:16
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-20 00:06:35
"""

import numpy as np


def C_state(num_qubits: int, threshold: int) -> np.ndarray:
    """Return the C state corresponding to the given number of qubits and the given threshold .

    :param num_qubits: [description]
    :type num_qubits: int
    :param threshold: [description]
    :type threshold: int
    :return: [description]
    :rtype: np.ndarray
    """
    state = np.zeros(2**num_qubits)

    ones: float = 0

    for i in range(2**num_qubits):
        if i < threshold:
            state[i] = 1
            ones += 1

    return state / np.sqrt(ones)
