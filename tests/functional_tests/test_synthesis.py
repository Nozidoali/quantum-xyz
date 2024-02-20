#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

import random
from itertools import combinations

import numpy as np
import pytest

from xyz import QState, quantize_state
from xyz import simulate_circuit
from xyz import prepare_state


def rand_state(num_qubit: int, sparsity: int, uniform: bool = False) -> QState:
    """Generate a random state .

    :param num_qubit: [description]
    :type num_qubit: int
    :return: [description]
    :rtype: QState
    """

    state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
        random.random() if not uniform else 1 for i in range(sparsity)
    ]
    np.random.shuffle(state_array)

    # normalize the state
    state_array = state_array / np.linalg.norm(state_array)

    return state_array


def place_ones(size, count):
    """Place one or more lists into one .

    :param size: [description]
    :type size: [type]
    :param count: [description]
    :type count: [type]
    :yield: [description]
    :rtype: [type]
    """
    for positions in combinations(range(size), count):
        p = [0] * size
        for i in positions:
            p[i] = 1
        yield p


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
        yield perm[:]


N_TESTS = 50

@pytest.fixture
def state_vectors():
    """Generate a random state vector for testing ."""
    all_state_vectors = []
    while len(all_state_vectors) < N_TESTS:
        num_qubit = random.randint(3, 4)
        sparsity = random.randint(num_qubit, 2 ** (num_qubit - 1) - 1)
        # sparsity = random.randint(2 ** (num_qubit - 1) - 1, 2 ** (num_qubit - 1) - 1)
        state = rand_state(num_qubit, sparsity, uniform=False)

        # check if the state is valid
        all_state_vectors.append(state)

    return all_state_vectors


def test_one_state(state_vectors):
    """Test one state.

    :param state_vector: [description]
    :type state_vector: [type]
    """

    for state_vector in state_vectors:
        state_vector_exp = state_vector
        target_state = quantize_state(state_vector_exp)
        # print("target state: ", target_state)

        circuit = prepare_state(target_state, verbose_level=0)

        # now we measure the distance between the target state and the actual state
        state_vector_act = simulate_circuit(circuit).data
        dist = np.linalg.norm(state_vector_act - state_vector_exp)

        assert dist**2 < 1e-1 # make sure the distance is small


if __name__ == "__main__":
    rand_state_vectors = []
    for i in range(100):
        num_qubit = random.randint(3, 3)
        sparsity = random.randint(num_qubit, 2 ** (num_qubit - 1) - 1)
        sparsity = random.randint(2 ** (num_qubit - 1) - 1, 2 ** (num_qubit - 1) - 1)
        state = rand_state(num_qubit, sparsity, uniform=False)
        rand_state_vectors.append(state)

    test_one_state(rand_state_vectors)
