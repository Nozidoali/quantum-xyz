#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:35:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:17:55
"""

from typing import Any
from .SearchBasedStateSynthesis import *
from Circuit import *

from typing import List


class SparseStateSynthesis(SearchBasedStateSynthesis):
    def __init__(self, target_state) -> None:
        SearchBasedStateSynthesis.__init__(self, target_state)

    def run(self) -> None:
        curr_state = self.target_state
        while True:
            print(f"remaining ones: {len(curr_state)}")
            if len(curr_state) == 1:
                break

            self.init_search()
            self.add_state(curr_state, cost=0)

            while not self.search_done():
                curr_cost, curr_state = self.state_queue.get()
                self.visit(curr_state)

                for next_state in self.get_next_states(curr_state):
                    self.add_state(next_state, cost=curr_cost + 1)
