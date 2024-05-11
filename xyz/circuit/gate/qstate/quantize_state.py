#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 10:08:01
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 10:08:21
"""

import numpy as np
from .qstate import QState


def quantize_state(state_vector: np.ndarray):
    """Quantize a state to the number of qubits .

    :param state_vector: a vector with 2**n entries, where n is the number of qubits.
    :type state_vector: np.ndarray
    """

    if isinstance(state_vector, QState):
        return state_vector

    if isinstance(state_vector, str):
        terms = state_vector.split("+")
        index_to_weight = {}
        for term in terms:
            coefficient, state = term.strip().split("*")
            coefficient = float(coefficient.strip())
            num_qubits = len(state.strip()[1:-1])
            index = int(state.strip()[1:-1], 2)
            index_to_weight[index] = coefficient
        return QState(index_to_weight, num_qubits)

    if not isinstance(state_vector, np.ndarray):
        state_vector = np.array(state_vector)

    # discard the imaginary part
    # state_vector = state_vector.real
    state_vector = np.real(state_vector)

    # normalize the vector
    state_vector = state_vector.astype(np.float64) / np.linalg.norm(
        state_vector.astype(np.float64)
    )

    index_to_weight = {}
    num_qubits = int(np.log2(len(state_vector)))
    for idx, coefficient in enumerate(state_vector):
        if not np.isclose(coefficient, 0):
            index_to_weight[idx] = coefficient
    return QState(index_to_weight, num_qubits)
