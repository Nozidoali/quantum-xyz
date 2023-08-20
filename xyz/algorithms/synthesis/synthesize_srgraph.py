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


def synthesize_srg(target_state: QState) -> SRGraph:
    """
    @brief Runs the search based state synthesis
    @param verbose Whether to print out the state of the search
    """

    srg = SRGraph(target_state.num_qubits)
    srg.init_search()

    curr_state = copy.deepcopy(target_state)

    srg.add_state(curr_state, cost=srg.get_lower_bound(curr_state))

    # This function is called by the search loop.
    while not srg.search_done():
        curr_cost, curr_state = srg.state_queue.get()
        srg.visit(curr_state)
        if curr_state.is_ground_state():
            # post-processing
            for i, pattern in enumerate(curr_state.patterns):
                if pattern == 0:
                    continue
                operator = XOperator(i)
                next_state = curr_state.apply_x(i)
                print(f"apply {operator} to {curr_state} -> {next_state}")
                srg.add_edge(curr_state, operator, next_state)
                curr_state = next_state
            break
        srg.explore(curr_cost, curr_state)
        if target_state in srg.record:
            prev_state, operator = srg.record[target_state]
            print(f"target_state = {target_state}, prev_state = {prev_state}, operator = {operator}")
            break
        assert target_state not in srg.record
        

    return srg
