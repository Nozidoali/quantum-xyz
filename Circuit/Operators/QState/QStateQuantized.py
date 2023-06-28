#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:50:44
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 10:53:40
"""

import numpy as np
from .QStateFramed import *


def quantize(state_array: np.ndarray, num_qubits: int) -> np.ndarray:
    """
    Quantize an array of states into a smaller number of states using a specified number of qubits.
    @param state_array - the array of states to be quantized
    @param num_qubits - the number of qubits to use for quantization
    @return The quantized states
    """
    quantized_states = []

    for i in range(2**num_qubits):
        if state_array[i] != 0:
            curr_state = 0
            for j in range(num_qubits):
                if (i >> j) & 1 == 1:
                    curr_state |= 1 << j

            quantized_states.append(curr_state)

    return quantized_states


class QStateQuantized(QStateFramed):
    def __init__(self, state_array: np.ndarray, num_qubits: int) -> None:
        quantized_state_array = quantize(state_array, num_qubits)
        QStateFramed.__init__(self, quantized_state_array, num_qubits)
