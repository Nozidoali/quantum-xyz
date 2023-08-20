#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

from gettext import find
import subprocess
import numpy as np

from xyz import (
    QState,
    synthesize_srg,
    stopwatch,
    from_val,
    lookup_repr,
)
from xyz.srgraph.operators.qstate.common.dicke_state import D_state


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
    # state = rand_state(4, 8)
    s = D_state(4, 2)
    state_val = 0
    for i in range(2**4):
        if s[i] != 0:
            state_val |= 1 << i
    state = from_val(state_val, 4)

    with stopwatch("synthesis"):
        srg = synthesize_srg(state, verbose=True)
    with open("srg.dot", "w") as f:
        f.write(str(srg))
    subprocess.run(["dot", "-Tpng", "srg.dot", "-o", "srg.png"])


if __name__ == "__main__":
    test_synthesis()
