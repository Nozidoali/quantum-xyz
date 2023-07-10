#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:35:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:17:55
"""

from typing import Any
from .CanonicalStateSynthesis import *
from ...Circuit import *
from typing import List
import subprocess

class SparseStateSynthesisParams:
    enable_step_by_step: bool = False

class SparseStateSynthesis(CanonicalStateSynthesis):
    def __init__(self, target_state: QState) -> None:
        """
        @brief Initializes the search based state synthesis. This is called by __init__ and should not be called directly
        @param target_state The state to synthesize from
        @return The synthesized state as a QState object or None if there was an error synthesizing
        """
        CanonicalStateSynthesis.__init__(self, target_state)

    def run(self, verbose: bool = False) -> QTransition:
        """
        @brief Runs the search based state synthesis
        @param verbose Whether to print out the state of the search
        """

        transitions = QTransition(self.num_qubits)

        num_visited_states: int = 0

        curr_state = self.target_state
        # This function is called by the search loop.
        while True:
            print(f"remaining ones: {len(curr_state)}")

            if verbose:
                print(f"curr_state: \n{curr_state}")

            if len(curr_state) == 1:
                break

            prev_ones = len(curr_state)

            self.init_search()
            self.add_state(curr_state, cost=self.get_lower_bound(curr_state))

            while not self.search_done():
                curr_cost, curr_state = self.state_queue.get()
                self.visit(curr_state)

                num_visited_states += 1

                # This function will break until we have a better state.
                if len(curr_state) == 1:
                    # we have found a better state
                    break

                if SparseStateSynthesisParams.enable_step_by_step and len(curr_state) < prev_ones:
                    break

                # Add next state to the list of states.
                for operator in self.get_ops(curr_state):
                    try:
                        next_state = operator(curr_state)
                        cost = operator.get_cost()
                        curr_astar_cost = self.get_lower_bound(curr_state)
                        astar_cost = self.get_lower_bound(next_state)

                        # This is buggy here, the correct function is shown below.
                        # However, the correct function is not working as good as this one.
                        # This is probably because we need to use MCRY instead of CNRY, and the cost function is incorrect.
                        #
                        # next_cost = curr_cost + cost + astar_cost - curr_astar_cost
                        next_cost = curr_cost + cost + astar_cost
                        success = self.add_state(next_state, cost=next_cost)

                        if success:
                            self.record_operation(curr_state, operator, next_state)
                    except:
                        continue

            assert self.is_visited(curr_state)
            assert len(curr_state) < prev_ones

            if verbose:
                print(f"num_visited_states: {num_visited_states}")
                
                state_index: int = 0
                for state in self.enquened_states:
                    state_index += 1
                    canonical_state, _ = get_representative(state, self.num_qubits)
                    state_cost = self.enquened_states[state] - self.get_lower_bound(state)
                    print(f"state{state_index}, cost = {state_cost}: \n{canonical_state}")
            
            curr_transitions = QTransition(self.num_qubits)
            state_before = curr_state
            for state, op in self.backtrace_state(state_before):

                if verbose:
                    print(
                        f"state: \n{state}\n\t, op = {op}, cost = {op.get_cost()}, state_before: {state_before}"
                    )
                curr_transitions.add_transition_to_back(state_before, ~op, state)
                state_before = state

            transitions = curr_transitions + transitions

        zero_state, initial_transitions = get_representative(
            curr_state, self.num_qubits
        )
        assert zero_state == ground_state(self.num_qubits)

        graph = self.export_record()
        graph.write("search_graph.dot")
        subprocess.call(["dot", "-Tpng", "search_graph.dot", "-o", "search_graph.png"])
        
        return initial_transitions + transitions
