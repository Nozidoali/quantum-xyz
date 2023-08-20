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

from xyz.srgraph import QState, SRGraph, XOperator, MCRYOperator, QuantizedRotationType
from xyz.srgraph.operators.operator import QOperator


def explore_state(srg: SRGraph, curr_state: QState, operator: QOperator, curr_cost: int) -> None:
    """Explore a state in a SRGraph .

    :param srg: [description]
    :type srg: SRGraph
    :param curr_state: [description]
    :type curr_state: QState
    :param operator: [description]
    :type operator: QOperator
    :param curr_cost: [description]
    :type curr_cost: int
    """
    
    next_state = operator(curr_state)
    next_cost = curr_cost + operator.get_cost() + srg.get_lower_bound(next_state) - srg.get_lower_bound(curr_state)
    
    # pre-processing
    next_state.cleanup_columns()
    
    # pre-processing Xs
    state = copy.deepcopy(next_state)
    x_signatures = next_state.get_x_signatures()
    for i in x_signatures:
        state = state.apply_x(i)
        
    # pre-processing Ys
    y_signatures = state.get_y_signatures()
    for i in y_signatures:
        state = state.apply_merge0(i)

    # we skip the state if it is already visited
    if state in srg.visited_states:
        return
    
    # we skip the state if it is already enquened and the cost is higher
    if state in srg.enquened_states and next_cost >= srg.enquened_states[state]:
        return
    
    # now we add the state to the queue
    srg.state_queue.put((next_cost, state))
    srg.enquened_states[state] = next_cost
    
    # and record the operator
    srg.record[state] = curr_state, operator
    
    return
    for i in x_signatures:
        state = next_state.apply_x(i)
        srg.record[state] = next_state, XOperator(i)
        next_state = state
    
    for i in y_signatures:
        state = next_state.apply_merge0(i)
        srg.record[state] = next_state, MCRYOperator(i, QuantizedRotationType.MERGE0, [], [])
        next_state = state
    
def synthesize_srg(target_state: QState, verbose: bool = False) -> SRGraph:
    """
    @brief Runs the search based state synthesis
    @param verbose Whether to print out the state of the search
    """

    srg = SRGraph(target_state.num_qubits)
    srg.init_search()

    print(f"target_state = {target_state}")
    
    curr_state = copy.deepcopy(target_state)

    curr_state.cleanup_columns()
    # pre-processing Xs
    x_signatures = curr_state.get_x_signatures()
    for i in x_signatures:
        next_state = curr_state.apply_x(i)
        srg.record[next_state] = curr_state, XOperator(i)
        curr_state = next_state
    
    curr_cost = srg.get_lower_bound(curr_state)
    srg.state_queue.put((curr_cost, curr_state))
    
    solution_reached: bool = False

    # This function is called by the search loop.
    while not srg.search_done():
        curr_state: QState
        curr_cost, curr_state = srg.state_queue.get()
        
        # print the progress bar
        if verbose:
            print(f"cost = {curr_cost}, visited = {len(srg.visited_states)}, in record: {len(srg.record)}", end="\r")
            sys.stdout.flush()

        # now we made sure that the state is canonical
        srg.visited_states.add(curr_state)
        
        if len(curr_state) == 0:
            # then we have found the solution
            solution_reached = True
            break

        for target_qubit in range(srg.num_qubits):
            pos_cofactor, neg_cofactor = curr_state.cofactors(target_qubit)

            # skip if the target qubit is already 1
            if curr_state.patterns[target_qubit] == 0:
                continue

            for control_qubit in range(srg.num_qubits):
                if control_qubit == target_qubit:
                    continue

                if curr_state.patterns[control_qubit] == 0:
                    continue

                for phase in [True, False]:

                    pos_cofactor, neg_cofactor = curr_state.controlled_cofactors(
                        target_qubit, control_qubit, phase
                    )

                    if len(pos_cofactor) > 0 and pos_cofactor == neg_cofactor:
                        
                        # apply merge0
                        quantum_operator = MCRYOperator(
                            target_qubit,
                            QuantizedRotationType.MERGE0,
                            [control_qubit],
                            [phase],
                        )
                        explore_state(srg, curr_state, quantum_operator, curr_cost)
                        
                        # apply merge1
                        quantum_operator = MCRYOperator(
                            target_qubit,
                            QuantizedRotationType.MERGE1,
                            [control_qubit],
                            [phase],
                        )
                        explore_state(srg, curr_state, quantum_operator, curr_cost)

                # CNOT
                for phase in [True]:
                    quantum_operator = MCRYOperator(
                        target_qubit, QuantizedRotationType.SWAP, [control_qubit], [phase]
                    )
                    explore_state(srg, curr_state, quantum_operator, curr_cost)        

    assert solution_reached
    assert QState.ground_state(srg.num_qubits) in srg.record

    print(f"cost = {curr_cost}, visited = {len(srg.visited_states)}, in record: {len(srg.record)}")
    
    return srg
