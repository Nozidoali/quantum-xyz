#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-10 19:24:34
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-10 22:25:33
"""

import copy

from xyz.circuit import QCircuit
from xyz.circuit import QState
from .ry_reduction import ry_reduction
from .x_reduction import x_reduction

ENABLE_Y_REDUCTION = True


def support_reduction(circuit: QCircuit, state: QState, enable_cnot: bool = True):
    """Apply the reduction to the circuit ."""
    new_state = copy.deepcopy(state)
    new_state, gates = x_reduction(circuit, new_state, enable_cnot)
    if ENABLE_Y_REDUCTION:
        new_state, y_gates = ry_reduction(circuit, new_state)
        gates += y_gates
    return new_state, gates[::-1]
