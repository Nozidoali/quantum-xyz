#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-21 21:50:06
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-21 22:37:44
"""

from typing import List, Tuple

from queue import PriorityQueue

import xyz.circuit as qc
from xyz.qstate import QState


class Library:
    """A library class .

    a library is linked to a set of operators when initialized .
    """

    def __init__(self) -> None:
        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enquened_states = {}
        self.record = {}
        self.num_qubits: int = None
        self.circuit: qc.QCircuit = None

    def explore_state(
        self, curr_state_pair: Tuple, next_state_pair: Tuple, gates: List
    ):
        """AI is creating summary for explore_state

        :param curr_state: [description]
        :type curr_state: QState
        """

        curr_cost, curr_state = curr_state_pair
        next_cost, next_state = next_state_pair

        next_state_repr = next_state.repr()

        # we skip the state if it is already visited
        if next_state_repr in self.visited_states:
            return None

        # we skip the state if it is already enquened and the cost is higher
        if (
            next_state_repr in self.enquened_states
            and next_cost >= self.enquened_states[next_state_repr]
        ):
            return None

        # now we add the state to the queue
        self.state_queue.put((next_cost, next_state))
        self.enquened_states[next_state_repr] = next_cost

        self.record[hash(next_state)] = hash(curr_state), gates[:]

    def initialize_queue(self, target_state: QState, circuit: qc.QCircuit):
        """Initialize the queue for the given state .

        :param target_state: [description]
        :type target_state: QState
        """

        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enquened_states = {}
        self.record = {}
        self.state_queue.put((0, target_state))
        self.num_qubits = target_state.num_qubits
        self.circuit = circuit

    def explore(self):
        """This method is called when the client is opened ."""
        raise NotImplementedError

    def get_solution(self):
        """This method is called when the client is closed ."""

        gates = []
        backtraced_states: set = set()
        curr_hash = hash(QState.ground_state(self.num_qubits))

        assert curr_hash in self.record

        while curr_hash in self.record:
            if curr_hash in backtraced_states:
                raise ValueError("Loop found")
            backtraced_states.add(curr_hash)
            prev_hash, _gates = self.record[curr_hash]
            for _gate in _gates:
                gates.append(_gate)
            curr_hash = prev_hash

        return gates
