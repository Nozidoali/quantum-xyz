#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:58:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:17:45
"""

from QuantumXYZ.Circuit import *
from .StateSynthesisBase import *

from queue import PriorityQueue
from typing import List


class SearchBasedStateSynthesis(StateSynthesisBase):
    def __init__(self, target_state: QStateBase) -> None:
        StateSynthesisBase.__init__(self, target_state)

        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enquened_states = {}
        self.record = {}

    def run(self) -> None:
        raise NotImplementedError

    def visit(self, state: QState) -> None:
        self.visited_states.add(state)

    def add_state(self, state: QState, cost: int) -> bool:
        if state in self.visited_states:
            return False

        if state in self.enquened_states and self.enquened_states[state] <= cost:
            return False

        self.state_queue.put((cost, state))
        self.enquened_states[state] = cost
        return True

    def init_search(self) -> None:
        self.visited_states.clear()
        self.state_queue = PriorityQueue()
        self.enquened_states.clear()
        self.record.clear()

    def record_operation(
        self, state_before: QState, op: QOperator, state_after: QState
    ) -> None:
        self.record[state_after] = state_before, op

    def search_done(self) -> bool:
        return self.state_queue.empty()

    def backtrace_state(self, state: QState):
        curr_state = state
        while curr_state in self.record:
            prev_state, op = self.record[curr_state]
            yield prev_state, op
            curr_state = prev_state

    def is_visited(self, state: QState):
        return state in self.visited_states

    def get_lower_bound(self, state: QState) -> int:
        """
        Get the lower bound for a given state in a QState object.
        @param state - the state for which to calculate the lower bound
        @return The lower bound as an integer
        """
        return 0

    def get_ops(self, state: QState):
        # yields the state of the pivot qubit.
        for pivot_qubit_index in range(self.num_qubits):
            # yields the rotation state of the current state.
            for rotation_type in [
                QuantizedRotationType.SWAP,
                QuantizedRotationType.MERGE0,
                QuantizedRotationType.MERGE1,
            ]:
                # first we try the case where no control qubit is used
                op = MCRYOperator(
                    target_qubit_index=pivot_qubit_index,
                    rotation_type=rotation_type,
                    control_qubit_indices=[],
                    control_qubit_phases=[],
                )

                yield op

                # Yields the state of the current state of the MCRY operator.
                for control_qubit_index in range(self.num_qubits):
                    # If control_qubit_index is pivot_qubit_index control_qubit_index pivot_qubit_index.
                    if control_qubit_index == pivot_qubit_index:
                        continue

                    # Yields the state of the current state.
                    for control_qubit_phase in [False, True]:
                        op = MCRYOperator(
                            target_qubit_index=pivot_qubit_index,
                            rotation_type=rotation_type,
                            control_qubit_indices=[control_qubit_index],
                            control_qubit_phases=[control_qubit_phase],
                        )

                        yield op
