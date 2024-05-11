#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 08:11:46
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 08:12:04
"""

import json
from .qstate import QState


def load_state(filename: str):
    """Loads the state of a given file .

    :param filename: [description]
    :type filename: str
    """

    # read the dict from the file
    with open(filename, "r", encoding="utf-8") as file:
        state_dict = json.load(file)

    num_qubits: int = None
    index_to_weight = {}
    for index_str, weight in state_dict.items():
        if num_qubits is None:
            num_qubits = len(index_str)

        index = int(index_str, 2)
        index_to_weight[index] = weight

    # convert the dict to a QState
    return QState(index_to_weight, num_qubits)


def from_val(val: int, num_qubits: int) -> QState:
    """Return the state from the vector representation .

    :param state_vector: [description]
    :type state_vector: np.ndarray
    :return: [description]
    :rtype: QState
    """

    assert 0 < val < 2 ** (2**num_qubits)
    states = []
    for i in range(2**num_qubits):
        if val & 1 == 1:
            states.append(i)
        val >>= 1

    patterns = [0 for i in range(num_qubits)]
    for _, value in enumerate(states):
        for j in range(num_qubits):
            patterns[j] = patterns[j] << 1 | ((value >> j) & 1)
    return QState(patterns, len(states))
