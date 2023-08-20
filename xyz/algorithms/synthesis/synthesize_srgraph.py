#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""

import copy
import sys

from xyz.srgraph import QState, SRGraph, XOperator


def synthesize_srg(target_state: QState, verbose: bool = False) -> SRGraph:
    """
    @brief Runs the search based state synthesis
    @param verbose Whether to print out the state of the search
    """

    srg = SRGraph(target_state.num_qubits)
    srg.init_search()

    curr_state = copy.deepcopy(target_state)
    print(f"target_state = {target_state}")

    srg.add_state(curr_state, cost=srg.get_lower_bound(curr_state))
    
    solution_reached: bool = False

    # This function is called by the search loop.
    while not srg.search_done():
        curr_cost, curr_state = srg.state_queue.get()
        if verbose:
            print(f"cost = {curr_cost}, visited = {len(srg.visited_states)}", end="\r")
            sys.stdout.flush()
        srg.visit(curr_state)
        if curr_state.is_ground_state():
            solution_reached = True
            break
        srg.explore(curr_cost, curr_state)

    assert solution_reached

    # post-processing
    to_negate = []
    for i, pattern in enumerate(curr_state.patterns):
        if pattern == 0:
            continue
        to_negate.append(i)
    
    # add edges
    for i in to_negate:
        operator = XOperator(i)
        next_state = curr_state.apply_x(i)
        print(f"apply {operator} to {curr_state} -> {next_state}")
        srg.record[next_state] = curr_state, operator
        curr_state = next_state

    assert QState.ground_state(srg.num_qubits) in srg.record
    
    return srg
