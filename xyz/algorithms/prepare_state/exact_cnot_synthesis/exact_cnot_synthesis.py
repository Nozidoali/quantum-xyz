#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

import numpy as np
from typing import List
from xyz.circuit import QCircuit
from xyz.circuit import QState

from ._astar import AStarCost
from ._backtrace import backtrace
from ._state_transitions import get_state_transitions
from .explorer import Explorer


def exact_cnot_synthesis(
    circuit: QCircuit,
    target_state: QState,
    verbose_level: int = 0,
    cnot_limit: int = None,
):
    """This function prepares the state by finding the shortest path ."""

    explorer = Explorer(verbose_level)
    explorer.add_state(target_state)

    # begin of the exact synthesis algorithm
    initial_state = QState.ground_state(target_state.num_qubits)

    curr_n, curr_m = len(target_state.get_supports()), target_state.get_sparsity()

    # This function is called by the search loop.
    solution_reached: bool = False
    while not explorer.is_done():
        curr_state: QState
        curr_cost: AStarCost
        curr_cost, curr_state = explorer.get_state()

        if verbose_level >= 2:
            print(f"curr_state: {curr_state}, cost: {curr_cost}")
            explorer.report()

        if cnot_limit is not None and curr_cost.cnot_cost > cnot_limit:
            # this will then raise an ValueError
            break

        if curr_state == initial_state:
            # then we have found the solution
            solution_reached = True
            break

        explorer.visit_state(curr_state)

        supports = curr_state.get_supports()
        _curr_n, _curr_m = len(supports), curr_state.get_sparsity()
        if curr_state.num_qubits > 4 and (_curr_n < curr_n or _curr_m < curr_m):
            curr_n, curr_m = _curr_n, _curr_m
            explorer.reset()

        transitions = get_state_transitions(circuit, curr_state, supports)
        for next_state, gates in transitions:
            explorer.explore_state(curr_state, gates, curr_cost, next_state)

    if not solution_reached:
        raise ValueError("No solution found")
    return backtrace(curr_state, explorer.record)
