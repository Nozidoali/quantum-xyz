#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-26 23:58:45
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-27 01:11:04
"""

# pylint: skip-file

from xyz import D_state
from xyz import quantize_state, MCRYOperator, QuantizedRotationType
from xyz import CTROperator
from xyz import TROperator
from xyz import QState


def test_operators():
    state = quantize_state([1, 1, 1, 0])
    quantum_operator = CTROperator(0, False, 1, False)
    next_state: QState = quantum_operator(state)
    assert 0b00 in next_state.index_set
    assert 0b10 in next_state.index_set
    assert 0b01 not in next_state.index_set
    assert 0b11 not in next_state.index_set


if __name__ == "__main__":
    test_operators()
