#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 12:11:13
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 18:33:47
"""

from typing import Any
from typing import List, Tuple


from .CnRyState import *

from enum import Enum, auto


class CnRYDirection(Enum):
    SWAP = auto()
    MERGE = auto()


class CnRyMove:
    def __init__(
        self,
        pivot_qubit: int,
        control_state: int,
        num_controls,
        control_states: List[Tuple],
        direction: CnRYDirection,
    ) -> None:
        self.pivot_qubit = pivot_qubit
        self.control_state = control_state
        self.num_controls = num_controls
        self.control_states = control_states[:]
        self.direction = direction

    def __str__(self) -> str:
        direction = "SWAP" if self.direction == CnRYDirection.SWAP else "MERGE"
        control_state = (
            "None" if self.control_state is None else f"{self.control_state:b}"
        )
        return f"CnRyMove({self.pivot_qubit}, {control_state}, {self.num_controls}, {self.control_states}, {direction})"

    def __call__(self, states: List[int]) -> Any:
        if isinstance(states, CnRyState):
            return move_to_neighbour(
                states, self.pivot_qubit, self.control_state, self.direction
            )

        new_states = set()

        for state in states:
            # check the unateness
            if (
                self.control_state is not None
                and (self.control_state >> state) & 1 == 0
            ):
                new_states.add(state)
                continue

            # zero to one, one to zero
            if self.direction == CnRYDirection.SWAP:
                new_states.add(state ^ (1 << self.pivot_qubit))

            # both
            if self.direction == CnRYDirection.MERGE:
                new_states.add(state)
                new_states.add(state ^ (1 << self.pivot_qubit))
                continue

        return new_states

    def __cost_function__(num_controls: int, direction: int):
        if num_controls == 0:
            return 0
        if direction == CnRYDirection.SWAP and num_controls == 1:
            return 1
        return 1 << num_controls

    def cost(self) -> int:
        return CnRyMove.__cost_function__(self.num_controls, self.direction)


def move_to_neighbour(
    curr_state: CnRyState,
    num_controls: int,
    pivot_qubit: int,
    control_state: int,
    direction: int,
) -> CnRyState:
    new_states = set()

    for state in curr_state.states:
        # check the unateness
        if control_state is not None and (control_state >> state) & 1 == 0:
            new_states.add(state)
            continue

        # get the neg state
        neg_state = state & (~(1 << pivot_qubit))
        pos_state = state | (1 << pivot_qubit)

        # we handle the case where both pos_state and neg_state are in the curr_state

        if state == neg_state and pos_state in curr_state.states:
            continue

        # zero to one, one to zero
        if direction == CnRYDirection.SWAP:
            if neg_state in curr_state.states and pos_state not in curr_state.states:
                new_states.add(pos_state)
            elif pos_state in curr_state.states and neg_state not in curr_state.states:
                new_states.add(neg_state)
            elif pos_state in curr_state.states and neg_state in curr_state.states:
                new_states.add(pos_state)
                new_states.add(neg_state)
            else:
                assert False
            continue

        # both
        if direction == CnRYDirection.MERGE:
            new_states.add(pos_state)
            new_states.add(neg_state)
            continue

    return CnRyState(list(new_states), curr_state.cost + num_controls)