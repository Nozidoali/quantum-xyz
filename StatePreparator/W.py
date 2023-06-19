#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-17 07:59:34
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-17 07:59:44
"""

import numpy as np

def W_state(num_qubits: int) -> np.ndarray:

    state = np.zeros(2 ** num_qubits)

    for i in range(num_qubits):
        state[(2 ** i)] = 1

    return state / np.sqrt(num_qubits)