#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""

import copy

from xyz.srgraph import QState, SRGraph, XOperator

def synthesize_srg(
    target_state: QState, enable_step_by_step: bool = False, verbose: bool = False
) -> SRGraph:
    """
    @brief Runs the search based state synthesis
    @param verbose Whether to print out the state of the search
    """

    srg = SRGraph(target_state.num_qubits)
    srg.init_search()

    curr_state = target_state
    
    srg.add_state(curr_state, cost=srg.get_lower_bound(curr_state))

    # This function is called by the search loop.
    while not srg.search_done():
        curr_cost, curr_state = srg.state_queue.get()
        srg.visit(curr_state)

        if curr_state.is_ground_state():
            break

        print(f"queue size: {srg.state_queue.qsize()}, enqueued states: {len(srg.enquened_states)}, visited states: {len(srg.visited_states)}")
        print(f"current cost: {curr_cost}, current state: {curr_state}")

        srg.explore(curr_cost, curr_state)
    
    print(f"done")
    return srg
