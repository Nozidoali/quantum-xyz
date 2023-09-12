#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

# pylint: skip-file

from ast import In
import random
import numpy as np
from itertools import combinations
from qiskit import Aer, transpile

from xyz import QState, cnot_synthesis, stopwatch, D_state, quantize_state, get_time
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


def test_synthesis():
    """Test that the synthesis is correct ."""

    state = rand_state(3, 4)

    # we first run baseline
    from baseline.baselines import run_sparse_state_synthesis, run_dd_based_method

    num_qubit, depth, cx = run_sparse_state_synthesis(state)
    print(f"baseline1: cx = {cx}")
    
    cx = run_dd_based_method(state)
    print(f"baseline2: cx = {cx}")

    target_state = quantize_state(state)

    with stopwatch("synthesis") as timer:
        try:
            circuit = cnot_synthesis(target_state, optimality_level=3, verbose_level=0)
        except ValueError:
            print(f"cannot cnot_synthesis state {target_state}")
            exit(1)

    circ = circuit.to_qiskit()
    print(circ)
    simulator = Aer.get_backend("qasm_simulator")
    transpiled = transpile(circ, basis_gates=["u", "cx"], optimization_level=0)
    cx = transpiled.count_ops().get("cx", 0)

    # print(f"{timer.time():0.02f} seconds")

    map_time = get_time("add_gate_mapped")
    # print(f"time mapping = {map_time}")

    # Run and get counts
    result = simulator.run(transpiled).result()
    counts = result.get_counts(transpiled)

    print(counts)
    print(f"ours: cx = {cx}")


if __name__ == "__main__":
    test_synthesis()
