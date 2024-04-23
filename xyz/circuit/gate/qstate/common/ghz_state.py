#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-17 07:54:26
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-17 07:59:22
"""


import numpy as np


def GHZ_state(num_qubits: int) -> np.ndarray:
    """Return a GHZ state .

    :param num_qubits: [description]
    :type num_qubits: int
    :return: [description]
    :rtype: np.ndarray
    """
    state = np.zeros(2**num_qubits)

    state[0] = 1
    state[-1] = 1

    return state / np.sqrt(2)
