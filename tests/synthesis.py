#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

import random
import numpy as np
from qiskit import Aer, transpile

from xyz import QState, synthesize, stopwatch, from_val, D_state


def rand_state(num_qubit: int, sparsity: int) -> QState:
    """Generate a random state .

    :param num_qubit: [description]
    :type num_qubit: int
    :return: [description]
    :rtype: QState
    """

    state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
        random.random() for i in range(sparsity)
    ]
    np.random.shuffle(state_array)
    return state_array


def test_synthesis():
    """Test that the synthesis is used ."""

    # state = rand_state(4, 5)
    state = D_state(6, 2)
    with stopwatch("synthesis"):
        circuit = synthesize(state, optimality_level=1)
        circ = circuit.to_qiskit()
        print(circ)
        simulator = Aer.get_backend("aer_simulator")
        circ = transpile(circ, simulator)

        # Run and get counts
        result = simulator.run(circ).result()
        counts = result.get_counts(circ)

        print(counts)
        print(f"cnot = {circ.count_ops()['cx']}")


if __name__ == "__main__":
    test_synthesis()
