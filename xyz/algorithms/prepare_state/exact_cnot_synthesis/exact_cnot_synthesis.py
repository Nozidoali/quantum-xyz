#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

from xyz.circuit import QCircuit
from xyz.circuit import QState

from ._astar import AStarCost
from ._backtrace import backtrace
from .state_transitions import get_state_transitions
from .explorer import Explorer

N_FRONT_MAX = 1e7
N_ENQUEUED_MAX = 1e6


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

    n_init, m_init = len(target_state.get_supports()), target_state.get_sparsity()
    best_state = target_state
    best_score = 0
    best_cost = AStarCost(0, explorer.get_lower_bound(target_state))

    # This function is called by the search loop.
    solution_reached: bool = False
    while not explorer.is_done():
        curr_state: QState
        curr_cost: AStarCost
        curr_cost, curr_state = explorer.get_state()
        n_cnot_at_front = explorer.get_n_front(curr_cost.cnot_cost)

        if verbose_level >= 2:
            print(f"curr_state: {curr_state}, cost: {curr_cost}")
            explorer.report()
            print(f"n_cnot_at_front: {n_cnot_at_front}")

        if n_cnot_at_front > N_FRONT_MAX or len(explorer.enqueued) > N_ENQUEUED_MAX:
            if best_score > 0:
                print(f"best_state: {best_state}, best_score: {best_score}")
                n_init, m_init = (
                    len(best_state.get_supports()),
                    best_state.get_sparsity(),
                )
                best_score = 0
                explorer.reset()
                explorer.add_state(best_state, best_cost)
                continue

        if cnot_limit is not None and curr_cost.cnot_cost > cnot_limit:
            # this will then raise an ValueError
            break

        if curr_state == initial_state:
            # then we have found the solution
            solution_reached = True
            break

        if curr_state.repr() in explorer.visited_states:
            continue

        explorer.visit_state(curr_state)

        supports = curr_state.get_supports()
        _curr_n, _curr_m = len(supports), curr_state.get_sparsity()
        curr_score = float(n_init * m_init - _curr_n * _curr_m) / (
            curr_cost.cnot_cost + 1
        )
        if curr_score > best_score:
            best_score = curr_score
            best_state = curr_state
            best_cost = curr_cost

        transitions = get_state_transitions(circuit, curr_state, supports)
        for next_state, gates in transitions:
            explorer.explore_state(curr_state, gates, curr_cost, next_state)

    if not solution_reached:
        raise ValueError("No solution found")
    return backtrace(curr_state, explorer.record)
