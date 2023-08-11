#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:58:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:17:45
"""

from queue import PriorityQueue
import stat
import pygraphviz as pgv

from xyz.circuit import QState, QStateBase, QOperator
from .canonicalization import get_representative
from ._canonical import (
    _add_state,
    _get_lower_bound,
    _visit,
    _is_visited,
    _get_operators,
)


class SearchEngine:
    """Generate the engine class ."""

    def __init__(self, target_state: QStateBase) -> None:
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
        return _visit(self, state)

    def add_state(self, state: QState, cost: int) -> bool:
        """Add a state to the machine .

        :param state: [description]
        :type state: QState
        :param cost: [description]
        :type cost: int
        :return: [description]
        :rtype: bool
        """
        return _add_state(self, state, cost)

    def init_search(self) -> None:
        """Initialize search state ."""
        self.visited_states.clear()
        self.state_queue = PriorityQueue()
        self.enquened_states.clear()
        self.record.clear()

    def record_operation(
        self, state_before: QState, op: QOperator, state_after: QState
    ) -> None:
        """Record a operation between state_after and state_after_after_after_after .

        :param state_before: [description]
        :type state_before: QState
        :param op: [description]
        :type op: QOperator
        :param state_after: [description]
        :type state_after: QState
        """
        self.record[state_after] = state_before, op

    def get_prev_state(self, state: QState) -> QState:
        """Get the previous state of a state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: QState
        """
        try:
            return self.record[state][0]
        except:
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
            prev_state, op = self.record[curr_state]
            yield prev_state, op
            curr_state = prev_state

    def is_visited(self, state: QState):
        """Returns whether the given state is visited .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        return _is_visited(self, state)

    @staticmethod
    def get_lower_bound(state: QState) -> int:
        """Returns the lower bound of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """
        return _get_lower_bound(state)

    def get_operators(self, state: QState):
        """Get the list of operators for the given state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        return _get_operators(self, state)
