#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-26 23:58:45
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-27 01:11:04
"""


from xyz import D_state
from xyz import quantize_state, MCRYOperator, QuantizedRotationType
from xyz.srgraph.operators.ctr import CTROperator
from xyz.srgraph.operators.tr import TROperator


def test_operators():
    state = [0.5, 0.5, 0.5, 0.0]

    state = quantize_state(state)

    print(state)
    quantum_operator = CTROperator(0, False, 1, False)
    next_state = quantum_operator(state)
    print(next_state)


if __name__ == "__main__":
    test_operators()
