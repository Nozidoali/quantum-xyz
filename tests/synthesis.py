#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

import subprocess
import numpy as np

from xyz import QState, synthesize_srg, D_state, stopwatch, get_time, representative_cache_hit, representative_cache_size


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


def test_synthesis():
    """Test that the synthesis is used ."""
    state = rand_state(4, 8)
    
    with stopwatch("synthesis"):
        srg = synthesize_srg(state, verbose=True)
    with open("srg.dot", "w") as f:
        f.write(str(srg))
    subprocess.run(["dot", "-Tpng", "srg.dot", "-o", "srg.png"])

if __name__ == "__main__":
    test_synthesis()
