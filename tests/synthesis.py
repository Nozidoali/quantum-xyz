#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

# pylint: skip-file

from math import floor
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
from xyz import HybridCnotSynthesisStatistics
from xyz.qstate.common import dicke_state
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


def test_synthesis(
    state_vector: np.ndarray, method: str = None, map_gates: bool = False
):
    """Test that the synthesis is correct ."""

    data = {}

    # we first run baseline
    from baseline.baselines import (
        run_sparse_state_synthesis,
        run_dd_based_method,
        run_sota_based_method,
    )

    if method == "m-flow":
        with stopwatch("baseline") as timer:
            num_qubit, depth, cx = run_sparse_state_synthesis(
                state_vector, skip_verify=True
            )
            data["cx"] = cx
            data["time"] = timer.time()

    elif method == "n-flow":
        with stopwatch("baseline") as timer:
            cx = run_dd_based_method(state_vector)
            data["cx"] = cx
            data["time"] = timer.time()

    elif method == "sota":
        with stopwatch("baseline") as timer:
            cx = run_sota_based_method(state_vector)
            data["cx"] = cx
            data["time"] = timer.time()

    elif method == "ours":

        target_state = quantize_state(state_vector)
        with stopwatch("synthesis") as timer:
            stats = HybridCnotSynthesisStatistics()
            circuit = hybrid_cnot_synthesis(
                target_state, map_gates=map_gates, stats=stats
            )
        stats.report()
        cx = circuit.get_cnot_cost()

        # circ = circuit.to_qiskit()
        # print(circ)
        # cx, equivalent = xyz.verify_circuit_and_count_cnot(
        #     circuit, state_vector, skip_verify=False
        # )

        data["cx"] = cx
        data["time"] = timer.time()
    return data


import pandas as pd

SPARSE = True
DICKE = False

if __name__ == "__main__":
    datas = []

    num_repeats: int = 100
    if DICKE:
        num_repeats = 1  # no need to repeat for dicke states

    for repeat in range(num_repeats):
        for num_qubits in range(3, 21):

            if DICKE:
                max_k = floor(num_qubits / 2)

                method = "sota"

                for k in range(1, max_k + 1):
                    state_vector = D_state(num_qubits, k)
                    data = test_synthesis(state_vector, method=method, map_gates=False)

                    data["num_qubits"] = num_qubits
                    data["k"] = k
                    data["method"] = method

                    datas.append(data)

                    df = pd.DataFrame(datas)
                    df.to_csv("data.csv", index=False)

            else:

                if SPARSE:
                    num_ones = num_qubits
                else:
                    num_ones = (1 << num_qubits) // 2

                if num_ones >= 2**num_qubits:
                    continue

                state_vector = rand_state(num_qubits, num_ones, uniform=True)
                # state_vector = D_state(num_qubits, k)

                list_of_method: list = None

                if SPARSE:
                    # list_of_method = ["n-flow", "m-flow", "ours"]
                    list_of_method = ["sota", "ours", "m-flow"]
                else:
                    # list_of_method = ["n-flow", "m-flow", "ours"]
                    list_of_method = ["sota"]

                for method in list_of_method:
                    data = test_synthesis(state_vector, method=method, map_gates=False)

                    data["num_qubits"] = num_qubits

                    if SPARSE:
                        data["cardinality"] = r"$m = n$"
                    else:
                        data["cardinality"] = r"$m = 2^{n-1}$"
                    data["method"] = method

                    # we insert three pieces of data

                    datas.append(data)

                    df = pd.DataFrame(datas)
                    df.to_csv("data.csv", index=False)
