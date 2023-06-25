#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 12:43:35
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 15:05:40
"""

from .Detail import *
from .XPClass import *
from queue import PriorityQueue
import logging


class CnRYSolver:
    def __init__(self, final_state_array: np.ndarray) -> None:
        self.final_state_array = final_state_array
        self.visited_states = set()
        self.enqueued_states = {}

        self.num_qubits = int(np.log2(len(final_state_array)))

        self.final_cardinality = np.count_nonzero(final_state_array)

        self.q = PriorityQueue()

        self.prev = {}
        self.final_state = to_cnry_state(self.final_state_array)
        self.final_equiv_state = self.final_state

        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler("cnry_solver.log")
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def add_initial_state(self) -> None:
        # two cases:
        # 1. final state is a pure state
        if self.final_cardinality == 1:
            initial_state = CnRyState()
            self.enqueued_states[initial_state] = initial_state.cost
            self.q.put(initial_state)
            self.prev[initial_state] = None, None

        # 2. initial_state is a mixed state
        else:
            initial_state = CnRyState()
            start_state = CnRyState([0, 1])

            move = CnRyMove(0, (1 << self.num_qubits) - 1, 0, [], CnRYDirection.MERGE)
            self.enqueued_states[start_state] = start_state.cost
            self.q.put(start_state)
            self.prev[start_state] = initial_state, move
            self.prev[initial_state] = None, None

    def add_final_state(self) -> None:
        # canonicalize the final state
        _, transitions = to_canonical_state(self.final_state.states, self.num_qubits)
        curr_state = self.update_transitions(self.final_state, transitions)
        self.final_equiv_state = curr_state

    def solve(self) -> None:
        self.add_initial_state()
        self.add_final_state()

        while not self.q.empty():
            curr_state = self.q.get()
            self.visited_states.add(curr_state)

            self.logger.info(f"Dequeue state {curr_state}, cost = {curr_state.cost}")

            if curr_state == self.final_equiv_state:
                print("Solution found, cost = ", curr_state.cost)
                return

            for qubit in range(self.num_qubits):
                moves = get_all_moves(self.num_qubits, qubit, 1)

                for move in moves:
                    new_state = move(curr_state)

                    state, transitions = to_canonical_state(
                        new_state.states, self.num_qubits
                    )
                    new_canonical_state = CnRyState(state, new_state.cost)

                    # this only works for the non-split
                    if len(new_canonical_state.states) > self.final_cardinality:
                        continue

                    if new_canonical_state in self.visited_states:
                        continue

                    if new_canonical_state in self.enqueued_states:
                        if (
                            new_canonical_state.cost
                            >= self.enqueued_states[new_canonical_state]
                        ):
                            continue

                    self.update_transitions(new_canonical_state, transitions)
                    self.enqueued_states[new_canonical_state] = new_canonical_state.cost
                    self.prev[new_state] = curr_state, move
                    self.q.put(new_canonical_state)

        logging.error("No solution found")
        raise Exception("No solution found")

    def update_transitions(
        self, current_state: CnRyState, transitions: List[Tuple[CnRyState, CnRyMove]]
    ) -> None:
        curr_state = CnRyState(current_state.states, current_state.cost)
        for transition in transitions:
            state, move = transition
            state = CnRyState(state)
            self.prev[state] = self.final_state, move

        return curr_state

    def retrieve_solution(self):
        print("Retrieving solution...")
        assert self.final_state in self.prev

        curr_state = self.final_state
        solution = []
        solution.append((curr_state, None))
        while curr_state != None:
            prev_state, move = self.prev[curr_state]
            print(curr_state)
            if prev_state != None:
                solution.append((prev_state, move))
            curr_state = prev_state

        return solution
