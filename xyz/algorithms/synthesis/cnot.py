#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""

from xyz.srgraph import QState, QTransition
from ._get_representative import get_representative
from ._search import SearchEngine

def cnot_synthesis(
    target_state: QState, enable_step_by_step: bool = False, verbose: bool = False
) -> QTransition:
    """
    @brief Runs the search based state synthesis
    @param verbose Whether to print out the state of the search
    """

    engine = SearchEngine(target_state)

    transitions = QTransition(target_state.num_qubits)

    num_visited_states: int = 0

    curr_state = target_state
    # This function is called by the search loop.
    while True:
        print(f"remaining ones: {len(curr_state)}")

        if verbose:
            print(f"curr_state: \n{curr_state}")

        if len(curr_state) == 1:
            break

        prev_ones = len(curr_state)

        engine.init_search()
        engine.add_state(curr_state, cost=engine.get_lower_bound(curr_state))

        while not engine.search_done():
            curr_cost, curr_state = engine.state_queue.get()
            engine.visit(curr_state)

            num_visited_states += 1

            # This function will break until we have a better state.
            if len(curr_state) == 0:
                # we have found a better state
                break

            if enable_step_by_step and len(curr_state) < prev_ones:
                break

            # Add next state to the list of states.
            for operator in engine.get_operators(curr_state):
                try:
                    next_state = operator(curr_state)
                    cost = operator.get_cost()

                    astar_cost = engine.get_lower_bound(next_state)

                    # This is buggy here, the correct function is shown below.
                    # However, the correct function is not working as good as this one.
                    # This is probably because we need to use MCRY instead of CNRY, and the cost function is incorrect.
                    #
                    # curr_astar_cost = engine.get_lower_bound(curr_state)
                    # next_cost = curr_cost + cost + astar_cost - curr_astar_cost
                    next_cost = curr_cost + cost + astar_cost
                    success = engine.add_state(next_state, cost=next_cost)

                    if success:
                        engine.record_operation(curr_state, operator, next_state)
                except ValueError:
                    continue

        assert engine.is_visited(curr_state)

        # start backtracing
        curr_transitions = QTransition(engine.num_qubits)
        state_before = curr_state
        for state, operator in engine.backtrace_state(state_before):
            if verbose:
                print(
                    f"state: \n{state}\n\t, op = {operator}, cost = {operator.get_cost()}, state_before: {state_before}"
                )
            curr_transitions.add_transition_to_back(state_before, ~operator, state)
            state_before = state

        transitions = curr_transitions + transitions

    return transitions
