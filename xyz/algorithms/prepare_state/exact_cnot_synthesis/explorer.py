#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-11 10:49:13
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-11 11:03:16
"""

from queue import PriorityQueue
from xyz.circuit import QState
from ._astar import AStarCost
from .precompute import QSPDatabase


class Explorer:
    def __init__(self, verbose_level: int = 0):
        # now we start the search
        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enqueued = {}
        self.record = {}
        self.verbose_level = verbose_level
        self.enqueued_states_of_cost = {}
        self.qsp_database = QSPDatabase(verbose_level)

    def get_lower_bound(self, state: QState):
        sub_index_to_weight = {}
        old_to_new_qubit_mapping = {}
        supports = state.get_supports()
        num_supports = len(supports)
        if num_supports != state.num_qubits:
            for new_index, old_index in enumerate(supports):
                old_to_new_qubit_mapping[old_index] = new_index
            for index, weight in state.index_to_weight.items():
                new_index: int = 0
                for i, support in enumerate(supports):
                    if index & (1 << support) != 0:
                        new_index |= 1 << i
                sub_index_to_weight[new_index] = weight
            new_state = QState(sub_index_to_weight, num_supports)
            return self.qsp_database.lookup(new_state)
        return self.qsp_database.lookup(state)

    def add_state(self, state: QState, cost: AStarCost = None):
        if cost is None:
            cost = AStarCost(0, self.get_lower_bound(state))
        self.state_queue.put((cost, state))
        self.enqueued[state.repr()] = cost

    def reset(self):
        self.state_queue = PriorityQueue()
        self.enqueued = {}
        self.visited_states = set()

    def visit_state(self, state: QState):
        self.visited_states.add(state.repr())

    def is_done(self):
        return self.state_queue.empty()

    def get_state(self):
        return self.state_queue.get()

    def get_n_front(self, n_cnot: int):
        if n_cnot not in self.enqueued_states_of_cost:
            return 0
        return self.enqueued_states_of_cost[n_cnot]

    def report(self):
        print(f"queue size: {self.state_queue.qsize()}")
        print(f"visited states: {len(self.visited_states)}")
        print(f"enqueued states: {len(self.enqueued)}")

    def explore_state(
        self,
        curr_state: QState,
        gates: list,
        curr_cost: AStarCost,
        next_state: QState = None,
    ) -> QState:
        """Explore a state in a transition graph."""

        if next_state is None:
            for gate in gates[::-1]:
                next_state = gate.conjugate().apply(curr_state)

        cnot_cost = sum([gate.get_cnot_cost() for gate in gates])
        next_cost = AStarCost(
            curr_cost.cnot_cost + cnot_cost,
            self.get_lower_bound(next_state),
        )
        repr_next = next_state.repr()

        # we skip the state if it is already visited
        if repr_next in self.visited_states:
            return None

        # we skip the state if it is already enquened and the cost is higher
        if repr_next in self.enqueued and next_cost >= self.enqueued[repr_next]:
            return None

        # now we add the state to the queue
        self.state_queue.put((next_cost, next_state))
        self.enqueued[repr_next] = next_cost

        if next_cost.cnot_cost not in self.enqueued_states_of_cost:
            self.enqueued_states_of_cost[next_cost.cnot_cost] = 0
        self.enqueued_states_of_cost[next_cost.cnot_cost] += 1

        # we record the gate
        gates_to_record: list = gates[:]

        # and record the quantum_operator
        if self.verbose_level >= 3:
            gates_str = ", ".join([str(gate) for gate in gates_to_record])
            print(f"recording [{next_state}] <- {curr_state}, gate: {gates_str}")
        self.record[hash(next_state)] = hash(curr_state), gates_to_record
        return next_state
