#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 16:33:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:21:23
"""

from cProfile import label
import operator
from queue import PriorityQueue
from time import process_time_ns
import pygraphviz as pgv
import copy

from .operators import QOperator, QState, QuantizedRotationType, MCRYOperator


class SRGraph:
    """Class method to call the transition class ."""

    def __init__(self, num_qubits: int) -> None:
        self.num_qubits = num_qubits

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
        self.visited_states.add(state.representative())

    def add_state(self, state: QState, cost: int) -> bool:
        """Add a state to the machine .

        :param state: [description]
        :type state: QState
        :param cost: [description]
        :type cost: int
        :return: [description]
        :rtype: bool
        """

        representive: QState = state.representative()

        if representive in self.visited_states:
            return False

        if (
            representive in self.enquened_states
            and self.enquened_states[representive] <= cost
        ):
            return False

        self.state_queue.put((cost, state))
        self.enquened_states[representive] = cost
        return True

    def init_search(self) -> None:
        """Initialize search state ."""
        self.visited_states.clear()
        self.state_queue = PriorityQueue()
        self.enquened_states.clear()
        self.record.clear()

    def add_edge(
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

    def backtrace_state(self, state: QState, max_depth: int = 100):
        """Return a generator that yields the operations from the given state .

        :param state: [description]
        :type state: QState
        :yield: [description]
        :rtype: [type]
        """
        curr_state = state
        curr_depth: int = 0
        while curr_state in self.record:
            # to avoid infinite loop
            if curr_depth > max_depth:
                raise RuntimeError(f"Backtrace depth exceeded state = {curr_state}")
            curr_depth += 1

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
        return state.representative() in self.visited_states

    @staticmethod
    def get_lower_bound(state: QState) -> int:
        """Returns the lower bound of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """
        return state.num_supports()

    def explore(self, cost: int, state: QState):
        """Return the neighbors of the state .

        :param state: [description]
        :type state: QState
        """

        for target_qubit in range(self.num_qubits):
            # skip if the target qubit is already 0
            if state.patterns[target_qubit] == 0:
                continue

            for control_qubit in range(self.num_qubits):
                if control_qubit == target_qubit:
                    continue

                if state.patterns[control_qubit] == 0:
                    continue

                # CNOT
                operator = MCRYOperator(
                    target_qubit, QuantizedRotationType.SWAP, [control_qubit], [True]
                )
                next_state = state.apply_cx(control_qubit, target_qubit)

                if not next_state < state:
                    continue

                next_cost = (
                    cost + operator.get_cost() + self.get_lower_bound(next_state)
                )
                if self.add_state(next_state, next_cost):
                    print(f"add edge: {state} -> {next_state} by {operator}")
                    self.add_edge(state, operator, next_state)

    def __str__(self) -> str:
        graph: pgv.AGraph = pgv.AGraph(directed=True)

        for state, edge in self.record.items():
            representative = state.representative()
            state_cost = self.enquened_states[representative]
            graph.add_node(
                str(state), label=f"[{state}]\n{representative}({state_cost})"
            )
            prev_state, edge_operator, *_ = edge
            graph.add_edge(
                str(prev_state),
                str(state),
                label=str(edge_operator) + f"({edge_operator.get_cost()})",
            )
        return graph.string()
