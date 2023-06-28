#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:58:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:17:45
"""

from Circuit import *
from .StateSynthesisBase import *

from queue import PriorityQueue
from typing import List


class SearchBasedStateSynthesis(StateSynthesisBase):
    def __init__(self, target_state: QStateBase) -> None:
        StateSynthesisBase.__init__(self, target_state)

        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enquened_states = {}

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

    def search_done(self) -> bool:
        return self.state_queue.empty()

    def get_next_states(self, curr_state: QState) -> List[QState]:
        raise NotImplementedError
