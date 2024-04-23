#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

import numpy as np
from typing import List
from queue import PriorityQueue
from xyz.circuit import QGate
from xyz.circuit import QCircuit, CX, CRY
from xyz.circuit import QState

from ._astar import AStarCost
from .support_reduction import support_reduction
from ._backtrace import backtrace
from .rotation_angles import get_ap_cry_angles


def exact_cnot_synthesis(
    circuit: QCircuit,
    target_state: QState,
    verbose_level: int = 0,
    cnot_limit: int = None,
):
    """This function prepares the state by finding the shortest path ."""

    # now we start the search
    visited_states = set()
    state_queue = PriorityQueue()
    enqueued = {}
    record = {}

    def map_qubit(qubit_index: int) -> int:
        return circuit.qubit_at(qubit_index)

    def explore_state(
        curr_state: QState,
        gates: List[QGate],
        curr_cost: AStarCost,
        next_state: QState = None,
    ) -> QState:
        """Explore a state in a SRGraph ."""
        nonlocal visited_states, state_queue, enqueued, record

        if next_state is None:
            for gate in gates[::-1]:
                next_state = gate.conjugate().apply(curr_state)
        cnot_cost = sum([gate.get_cnot_cost() for gate in gates])
        next_cost = AStarCost(
            curr_cost.cnot_cost + cnot_cost,
            next_state.get_lower_bound(),
        )
        repr_next = next_state.repr()

        # we skip the state if it is already visited
        if repr_next in visited_states:
            return None
        # we skip the state if it is already enquened and the cost is higher
        if repr_next in enqueued and next_cost >= enqueued[repr_next]:
            return None

        # now we add the state to the queue
        state_queue.put((next_cost, next_state))
        enqueued[repr_next] = next_cost

        # we record the gate
        gates_to_record: List[QGate] = gates[:]

        # and record the quantum_operator
        if verbose_level >= 3:
            gates_str = ", ".join([str(gate) for gate in gates_to_record])
            print(f"recording [{next_state}] <- {curr_state}, gate: {gates_str}")
        record[hash(next_state)] = hash(curr_state), gates_to_record
        return next_state

    # begin of the exact synthesis algorithm
    initial_state = QState.ground_state(target_state.num_qubits)

    curr_state = target_state
    curr_cost = AStarCost(0, curr_state.get_lower_bound())
    state_queue.put((curr_cost, curr_state))
    solution_reached: bool = False

    # This function is called by the search loop.
    while not state_queue.empty():
        curr_state: QState
        curr_cost: AStarCost
        curr_cost, curr_state = state_queue.get()

        if verbose_level >= 2:
            print(f"\n\ncurr_state: {curr_state}, cost: {curr_cost}")

        if cnot_limit is not None and curr_cost.cnot_cost > cnot_limit:
            # this will then raise an ValueError
            break

        if curr_state == initial_state:
            # then we have found the solution
            solution_reached = True
            break

        curr_state_repr = curr_state.repr()
        visited_states.add(curr_state_repr)
        supports = curr_state.get_supports()

        search_done = False

        # try dependency analysis
        new_state, gates = support_reduction(circuit, curr_state)
        if len(gates) > 0:
            curr_state = explore_state(curr_state, gates, curr_cost, new_state)
            search_done = True

        if not search_done:
            # apply CRY
            for target_qubit in supports:
                for control_qubit in supports:
                    if control_qubit == target_qubit:
                        continue
                    for phase in [True, False]:
                        cry_angle = get_ap_cry_angles(
                            curr_state, control_qubit, target_qubit, phase
                        )
                        if cry_angle is None:
                            continue
                        explore_state(
                            curr_state,
                            [
                                CRY(
                                    cry_angle,
                                    map_qubit(control_qubit),
                                    phase,
                                    map_qubit(target_qubit),
                                )
                            ],
                            curr_cost,
                        )
                        explore_state(
                            curr_state,
                            [
                                CRY(
                                    cry_angle - np.pi,
                                    map_qubit(control_qubit),
                                    phase,
                                    map_qubit(target_qubit),
                                )
                            ],
                            curr_cost,
                        )

            # apply CNOT
            for target_qubit in supports:
                for control_qubit in supports:
                    if control_qubit == target_qubit:
                        continue
                    for phase in [True, False]:
                        gate = CX(
                            map_qubit(control_qubit), phase, map_qubit(target_qubit)
                        )
                        explore_state(curr_state, [gate], curr_cost)

    if not solution_reached:
        raise ValueError("No solution found")
    return backtrace(curr_state, record)
