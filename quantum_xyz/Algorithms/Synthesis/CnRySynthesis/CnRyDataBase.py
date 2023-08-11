#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 15:20:10
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 18:35:13
"""

from typing import List

from .Detail import *
from queue import PriorityQueue
from .XPClass import *
from quantum_xyz.Utils import *
import numpy as np


class CnRyDataBaseEntryPoint:
    """
    This class is used to store the entry point of CnRyDataBase.
    """

    def __init__(self, state_list: List[int]) -> None:
        self.states: List[int] = state_list

    def apply(self, move: CnRyMove) -> "CnRyDataBaseEntryPoint":
        """
        Apply a move to the current state and return a new entry point.
        @param move - the move to apply
        @return a new entry point with the updated state
        """
        return CnRyDataBaseEntryPoint(move(self.states))

    def __eq__(self, __value: object) -> bool:
        states1 = sorted(self.states)
        states2 = sorted(__value.states)

        if len(states1) != len(states2):
            return False

        for i in range(len(states1)):
            if states1[i] != states2[i]:
                return False

        return True

    def __sub__(self, other: "CnRyDataBaseEntryPoint") -> int:
        diff1: int = 0
        diff2: int = 0

        for i in range(len(self.states)):
            if self.states[i] not in other.states:
                diff1 += 1

        for i in range(len(other.states)):
            if other.states[i] not in self.states:
                diff2 += 1

        return max(diff1, diff2)

    def __lt__(self, other: "CnRyDataBaseEntryPoint") -> bool:
        return lt(self.states, other.states)

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.states)))

    def __str__(self) -> str:
        return "-".join([f"{state:b}" for state in self.states])

    def canonicalize(self) -> "CnRyDataBaseEntryPoint":
        """
        This method canonicalizes the current entry point.
        """
        num_qubits = (
            int(np.ceil(np.log2(float(max(self.states) + 1))))
            if max(self.states) > 0
            else 0
        )
        state, transitions = to_canonical_state(self.states, num_qubits)
        return CnRyDataBaseEntryPoint(state), transitions


class CnRyDateBaseNode:
    def __init__(
        self,
        key: CnRyDataBaseEntryPoint,
        prev: "CnRyDateBaseNode",
        move_from_prev: CnRyMove,
        canonical_transitions: List[Tuple[List[int], CnRyMove]],
        cost: int,
    ) -> None:
        self.key = key
        self.prev = prev
        self.move_from_prev = move_from_prev
        self.canonical_transitions = canonical_transitions

        self.cost = cost

    def __lt__(self, other: "CnRyDateBaseNode") -> bool:
        return self.cost < other.cost


class CnRyDataBase:
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits

        self.look_up_table = {}

    def construct(self, target_entry_point: CnRyDataBaseEntryPoint = None):
        if not isinstance(target_entry_point, CnRyDataBaseEntryPoint):
            target_entry_point = CnRyDataBaseEntryPoint(target_entry_point)
        target_entry_point, _ = target_entry_point.canonicalize()
        with stopwatch("constructing database"):
            self.initialize(target_entry_point=target_entry_point)

    def initialize(self, target_entry_point: CnRyDataBaseEntryPoint = None):
        """
        This code appears to be part of a class method that initializes a database. The method initializes the database by creating an initial entry point and node, and adding them to a lookup table. It then creates a priority queue and a set of visited nodes.
        """
        initial_entry_point = CnRyDataBaseEntryPoint([0])
        initial_node = CnRyDateBaseNode(initial_entry_point, None, None, [], 0)

        # construct priority queue
        q = PriorityQueue()
        visited = set()
        enqueued_entries: dict = {}

        # push initial node into priority queue
        q.put(initial_node)

        terminate_cost: int = None
        terminate_node: CnRyDateBaseNode = None

        while not q.empty():
            curr_node = q.get()
            curr_entry_point = curr_node.key

            if target_entry_point is not None:
                if curr_entry_point == target_entry_point:
                    return

                if terminate_cost is not None and curr_node.cost >= terminate_cost:
                    self.look_up_table[target_entry_point] = terminate_node
                    return

            if curr_entry_point in visited:
                continue

            visited.add(curr_entry_point)

            # only the first time we see this entry point, we add it to the look up table
            if curr_entry_point not in self.look_up_table:
                self.look_up_table[curr_entry_point] = curr_node

            # get all possible moves
            possible_moves = get_all_cnot_moves(self.num_qubits)

            for move in possible_moves:
                # get the next entry point
                next_entry_point: CnRyDataBaseEntryPoint = curr_entry_point.apply(move)

                # if the next entry point is None, we need to skip
                if next_entry_point is None:
                    continue

                canonicalized_entry_point, transitions = next_entry_point.canonicalize()

                if canonicalized_entry_point in visited:
                    continue

                # compute the new cost
                # we can do a A start search here
                new_cost = curr_node.cost + move.cost()

                if target_entry_point is not None:
                    new_cost += target_entry_point - canonicalized_entry_point

                    if target_entry_point < canonicalized_entry_point:
                        continue

                    if canonicalized_entry_point == target_entry_point:
                        if terminate_cost is None or new_cost < terminate_cost:
                            terminate_cost = new_cost
                            terminate_node = CnRyDateBaseNode(
                                canonicalized_entry_point,
                                curr_node,
                                move,
                                transitions,
                                terminate_cost,
                            )

                if canonicalized_entry_point in enqueued_entries:
                    if new_cost >= enqueued_entries[canonicalized_entry_point]:
                        continue

                # create a new node
                new_node = CnRyDateBaseNode(
                    canonicalized_entry_point, curr_node, move, transitions, new_cost
                )
                enqueued_entries[canonicalized_entry_point] = new_cost
                q.put(new_node)

    def lookup(self, state: List[int]):
        """
        This method looks up the given state in the database and returns the corresponding node.
        @param state - the state to look up
        @return the node corresponding to the given state
        """
        tracer = WeightTracer(num_qubits=self.num_qubits, initial_state=state)

        entry_point, postprocessing = CnRyDataBaseEntryPoint(state).canonicalize()

        assert isinstance(postprocessing, list)

        for transition in postprocessing:
            state_before, move, state_after = transition

            logging.debug(f"Transition: {state_after} <- {state_before}, move = {move}")
            tracer.trace(state_after, move)

        if entry_point not in self.look_up_table:
            return None

        curr_node = self.look_up_table[entry_point]

        while curr_node != None:
            prev_node = curr_node.prev
            transitions = curr_node.canonical_transitions

            if prev_node is not None:
                prev_state = curr_node.key.states

                for transition in transitions:
                    state_before, move, state_after = transition

                    logging.debug(
                        f"Transition: {state_after} <- {state_before}, move = {move}"
                    )
                    tracer.trace(state_before, move)
                    prev_state = state_before

                move = curr_node.move_from_prev

                logging.debug(f"state: {prev_state} <- {prev_node.key}, move = {move}")

                tracer.trace(prev_node.key.states, move)

            curr_node = prev_node

        return tracer.export()
