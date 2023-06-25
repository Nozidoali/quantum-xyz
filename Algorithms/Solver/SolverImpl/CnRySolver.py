#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-25 12:43:35
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 13:13:17
'''

from .Detail import *
from queue import PriorityQueue
import logging

class CnRYSolver:

    def __init__(self, final_state: np.ndarray) -> None:
        self.final_state = final_state
        self.visited_states = set()
        self.enqueued_states = {}

        self.num_qubits = int(np.log2(len(final_state)))
        
        self.final_cardinality = np.count_nonzero(final_state)
        
        self.q = PriorityQueue()

        self.prev = {}
        
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

            move = CnRyMove(0, (1<<self.num_qubits)-1, 0, [], CnRYDirection.MERGE)
            self.enqueued_states[start_state] = start_state.cost
            self.q.put(start_state)
            self.prev[start_state] = initial_state, move
            self.prev[initial_state] = None, None


    def solve(self) -> None:
        
        self.add_initial_state()

        while not self.q.empty():
            curr_state = self.q.get()
            self.visited_states.add(curr_state)

            if curr_state == to_cnry_state(self.final_state):
                print("Solution found, cost = ", curr_state.cost)
                return
            
            for qubit in range(self.num_qubits):
                moves = get_all_moves(self.num_qubits, qubit, 1)

                for move in moves:
                    new_state = move(curr_state)

                    # this only works for the non-split
                    if len(new_state.states) > self.final_cardinality:
                        continue
                    
                    if new_state in self.visited_states:
                        continue
                    
                    if new_state in self.enqueued_states:
                        if new_state.cost >= self.enqueued_states[new_state]:
                            continue

                    self.enqueued_states[new_state] = new_state.cost
                    self.prev[new_state] = curr_state, move
                    self.q.put(new_state)

        logging.error("No solution found")
        raise Exception("No solution found")
    
    def retrieve_solution(self):
        
        final_cnry_state = to_cnry_state(self.final_state)
        assert final_cnry_state in self.prev

        curr_state = final_cnry_state
        solution = []
        solution.append((curr_state, None))
        while curr_state != None:
            prev_state, move = self.prev[curr_state]
            if prev_state != None:
                solution.append((prev_state, move))
            curr_state = prev_state
        
        return solution