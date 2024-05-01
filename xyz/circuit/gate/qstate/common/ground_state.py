#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-17 07:59:34
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-17 07:59:44
"""

import numpy as np

def ground_state(num_qubits: int) -> np.array:
    """W state
    """
    state = np.zeros(2**num_qubits)

    state[0] = 1

    return np.array(state)
