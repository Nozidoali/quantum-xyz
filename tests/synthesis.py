#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

import numpy as np
from qiskit import Aer, transpile

from xyz import (
    QState,
    synthesize,
    stopwatch,
    from_val,
    D_state
)

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
    state_val = 0
    for i in range(2**num_qubit):
        if state_array[i] == 1:
            state_val |= 1 << i

    return from_val(state_val, num_qubit)


def test_synthesis():
    """Test that the synthesis is used ."""

    state = D_state(4, 2)

    with stopwatch("synthesis"):
        circuit = synthesize(state, verbose_level=2)
        circ = circuit.to_qiskit()
        print(circ)
        simulator = Aer.get_backend('aer_simulator')
        circ = transpile(circ, simulator)

        # Run and get counts
        result = simulator.run(circ).result()
        counts = result.get_counts(circ)
        
        print(counts)
if __name__ == "__main__":
    test_synthesis()
