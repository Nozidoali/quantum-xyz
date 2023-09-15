#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

# pylint: skip-file

import random
import numpy as np
from itertools import combinations
from qiskit import Aer, transpile

import xyz
from xyz import (
    QState,
    hybrid_cnot_synthesis,
    stopwatch,
    D_state,
    quantize_state,
    get_time,
)
from xyz.utils.colors import print_red, print_yellow


def rand_state(num_qubit: int, sparsity: int, uniform: bool = True) -> QState:
    """Generate a random state .

    :param num_qubit: [description]
    :type num_qubit: int
    :return: [description]
    :rtype: QState
    """

    if uniform:
        state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
            1 for i in range(sparsity)
        ]
    else:
        state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
            random.random() for i in range(sparsity)
        ]
    np.random.shuffle(state_array)

    # now we need to normalize the state
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


def test_synthesis(state_vector: np.ndarray, map_gates: bool = False):
    """Test that the synthesis is correct ."""

    data = {}

    # we first run baseline
    from baseline.baselines import run_sparse_state_synthesis, run_dd_based_method

    num_qubit, depth, cx = run_sparse_state_synthesis(state_vector, skip_verify=False)
    data["baseline_density"] = cx

    cx = run_dd_based_method(state_vector)
    data["baseline_qubit"] = cx

    target_state = quantize_state(state_vector)

    with stopwatch("synthesis") as timer:
        circuit = hybrid_cnot_synthesis(target_state, map_gates=map_gates)

    circ = circuit.to_qiskit()
    # print(circ)
    cx, equivalent = xyz.verify_circuit_and_count_cnot(
        circuit, state_vector, skip_verify=False
    )

    if not equivalent:
        from tests.regression_tests import save_buggy_state

        save_buggy_state(quantize_state(state_vector))

    data["ours"] = cx

    return data


import pandas as pd


if __name__ == "__main__":
    datas = []

    for repeat in range(10):
        for num_qubits in range(3, 20):
            for sparsity in range(1, 2):
                num_ones: int = int(
                    (num_qubits**sparsity) / np.math.factorial(sparsity)
                )

                if num_ones >= 2**num_qubits:
                    continue

                state_vector = rand_state(num_qubits, num_ones, uniform=True)
                data = test_synthesis(state_vector, map_gates=True)

                data["num_qubits"] = num_qubits
                data["sparsity"] = sparsity

                datas.append(data)

                df = pd.DataFrame(datas)
                df.to_csv("data.csv", index=False)
