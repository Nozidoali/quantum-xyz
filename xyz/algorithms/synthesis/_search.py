#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:58:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:17:45
"""

from queue import PriorityQueue

from xyz.srgraph import QState, QOperator, MCRYOperator, QuantizedRotationType
from ._get_representative import get_representative

class SearchEngine:
    """Generate the engine class ."""

    def __init__(self, target_state: QState) -> None:
        self.target_state = target_state
        self.num_qubits = target_state.num_qubits

        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enquened_states = {}
        self.record = {}

    def visit(self, state: QState) -> None:
        """Visit the current state and return the result .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        state_repr, _ = get_representative(state, self.num_qubits)
        self.visited_states.add(state_repr)

    def add_state(self, state: QState, cost: int) -> bool:
        """Add a state to the machine .

        :param state: [description]
        :type state: QState
        :param cost: [description]
        :type cost: int
        :return: [description]
        :rtype: bool
        """
        state_repr, _ = get_representative(state, self.num_qubits)

        if state_repr in self.visited_states:
            return False

        if state_repr in self.enquened_states and self.enquened_states[state_repr] <= cost:
            return False

        self.state_queue.put((cost, state))
        self.enquened_states[state_repr] = cost
        return True

    def init_search(self) -> None:
        """Initialize search state ."""
        self.visited_states.clear()
        self.state_queue = PriorityQueue()
        self.enquened_states.clear()
        self.record.clear()

    def record_operation(
        self, state_before: QState, operator: QOperator, state_after: QState
    ) -> None:
        """Record a operation between state_after and state_after_after_after_after .

        :param state_before: [description]
        :type state_before: QState
        :param operator: [description]
        :type operator: QOperator
        :param state_after: [description]
        :type state_after: QState
        """
        self.record[state_after] = state_before, operator

    def get_prev_state(self, state: QState) -> QState:
        """Get the previous state of a state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: QState
        """
        try:
            return self.record[state][0]
        except KeyError:
            return None

    def search_done(self) -> bool:
        """Return True if all search is done .

        :return: [description]
        :rtype: bool
        """
        return self.state_queue.empty()

    def backtrace_state(self, state: QState):
        """Return a generator that yields the operations from the given state .

        :param state: [description]
        :type state: QState
        :yield: [description]
        :rtype: [type]
        """
        curr_state = state
        while curr_state in self.record:
            prev_state, operator = self.record[curr_state]
            yield prev_state, operator
            curr_state = prev_state

    def is_visited(self, state: QState):
        """Returns whether the given state is visited .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        state_repr, _ = get_representative(state, self.num_qubits)
        return state_repr in self.visited_states
    
    @staticmethod
    def get_lower_bound(state: QState) -> int:
        """Returns the lower bound of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """
        return state.num_supports()

    def get_operators(self, state: QState):
        """Get the list of operators for the given state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        one_counts = state.count_ones()

        # yields the state of the pivot qubit.
        for pivot_qubit_index in range(self.num_qubits):
            # this qubit is a dont care qubit.
            if one_counts[pivot_qubit_index] == 0 or one_counts[pivot_qubit_index] == len(
                state
            ):
                continue

            # yields the rotation state of the current state.
            for rotation_type in [
                QuantizedRotationType.SWAP,
                QuantizedRotationType.MERGE0,
            ]:
                # first we try the case where no control qubit is used
                operator = MCRYOperator(
                    target_qubit_index=pivot_qubit_index,
                    rotation_type=rotation_type,
                    control_qubit_indices=[],
                    control_qubit_phases=[],
                )

                yield operator

                if rotation_type == QuantizedRotationType.MERGE0:
                    continue

                # Yields the state of the current state of the MCRY operatorerator.
                for control_qubit_index in range(self.num_qubits):
                    # If control_qubit_index is pivot_qubit_index control_qubit_index pivot_qubit_index.
                    if control_qubit_index == pivot_qubit_index:
                        continue

                    # Yields the state of the current state.
                    operator = MCRYOperator(
                        target_qubit_index=pivot_qubit_index,
                        rotation_type=rotation_type,
                        control_qubit_indices=[control_qubit_index],
                        control_qubit_phases=[True],
                    )

                    yield operator
