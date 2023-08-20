#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 19:41:07
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:34:14
"""

import numpy as np

from xyz import QState, D_state
from xyz.utils.timer import get_time


def rand_state(num_qubit: int, sparsity: int) -> QState:
    """Generate a random state .

    :param num_qubit: [description]
    :type num_qubit: int
    :return: [description]
    :rtype: QState
    """

    state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
        1 for i in range(sparsity)
    ]
    np.random.shuffle(state_array)
    return QState(np.array(state_array), num_qubit)


def test_canonicalization():
    """Test that the canonicalization is used ."""
    # state = rand_state(3, 3)
    state = QState(D_state(5, 2), 5)
    print(f"before: {state}")

    state = state.representative()
    print(f"after: {state}")
    print(f"time = {get_time('representative')}")

if __name__ == "__main__":
    test_canonicalization()
