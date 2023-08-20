#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 19:41:07
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:34:14
"""

import numpy as np
from itertools import permutations, combinations

from xyz import QState, D_state, get_time, representative, representative_old


def place_ones(size, count):
    for positions in combinations(range(size), count):
        p = [0] * size
        for i in positions:
            p[i] = 1
        yield p


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


def all_states(num_qubit: int, sparsity: int) -> QState:
    """Return a QState with all states of the given number of qubit .

    :param num_qubit: [description]
    :type num_qubit: int
    :param sparsity: [description]
    :type sparsity: int
    :return: [description]
    :rtype: QState
    """
    for perm in place_ones(2**num_qubit, sparsity):
        yield QState(np.array(perm[:]), num_qubit)


def test_canonicalization():
    """Test that the canonicalization is used ."""
    # state = rand_state(3, 3)
    num_qubit: int = 4
    num_ppp_classes = {}
    for sparsity in range(1, 2**num_qubit):
        canon_states = set()
        for idx, state in enumerate(all_states(num_qubit, sparsity)):
            state = representative_old(state)
            canon_states.add(state)

        print(f"sparsity = {sparsity}, num_ppp_classes = {len(canon_states)}")
        num_ppp_classes[sparsity] = len(canon_states)

        # for state in canon_states:
        #     print(state)
    print(num_ppp_classes)


if __name__ == "__main__":
    test_canonicalization()
