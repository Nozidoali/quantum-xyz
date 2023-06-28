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
from QuantumXYZ import *

from typing import List


class SparseStateSynthesis(CanonicalStateSynthesis):
    def __init__(self, target_state: QState) -> None:
        """
         @brief Initializes the search based state synthesis. This is called by __init__ and should not be called directly
         @param target_state The state to synthesize from
         @return The synthesized state as a QState object or None if there was an error synthesizing
        """
        CanonicalStateSynthesis.__init__(self, target_state)

    def run(self) -> None:
        """
         @brief Runs the Bayesian network. This is the main loop of the Bayesian network. It will loop until there is nothing left to do
        """
        
        transitions = QTransition(self.num_qubits)

        curr_state = self.target_state
        # This function is called by the search loop.
        while True:
            print(f"remaining ones: {len(curr_state)}")

            if len(curr_state) == 1:
                break

            prev_ones = len(curr_state)

            self.init_search()
            self.add_state(curr_state, cost=0)

            while not self.search_done():
                curr_cost, curr_state = self.state_queue.get()
                self.visit(curr_state)

                # This function will break until we have a better state.
                if len(curr_state) < prev_ones:
                    # we have found a better state
                    break

                # Add next state to the list of states.
                for operator in self.get_ops(curr_state):

                    try:
                        next_state = operator(curr_state)
                        cost = operator.get_cost()
                        success = self.add_state(next_state, cost=curr_cost + cost)
                        
                        if success:
                            self.record_operation(curr_state, operator, next_state)
                    except:
                        continue
            
            assert self.is_visited(curr_state)

            curr_transitions = QTransition(self.num_qubits)
            state_before = curr_state
            for state, op in self.backtrace_state(state_before):
                print(f"state: {state}, cost = {op.get_cost()}, state_before: {state_before}")
                curr_transitions.add_transition_to_back(state_before, ~op, state)
                state_before = state
        
            transitions = curr_transitions + transitions
        
        zero_state, initial_transitions = get_representative(curr_state, self.num_qubits)
        assert zero_state == ground_state(self.num_qubits)

        return initial_transitions + transitions
