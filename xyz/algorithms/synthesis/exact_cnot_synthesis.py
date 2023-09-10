#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

import time
from queue import PriorityQueue
import numpy as np
from xyz.algorithms.synthesis import ground_state_calibration
from xyz.circuit.basic_gates.base.gate import QGate
from xyz.circuit.basic_gates.cx import CX
from xyz.circuit import QCircuit, X, MCRY
from xyz.srgraph import (
    QState,
    SRGraph,
    QOperatorType,
    QOperator,
    TROperator,
    XOperator,
    CXOperator,
    CTROperator,
    quantize_state,
)

from .ground_state_calibration import ground_state_calibration


class AStarCost:
    """AStarCost class ."""

    def __init__(
        self, cnot_cost: float, unitary_cost: float, lower_bound: float
    ) -> None:
        self.cnot_cost = cnot_cost
        self.unitary_cost = unitary_cost
        self.lower_bound = lower_bound

    def __lt__(self, other):
        return (
            self.cnot_cost + 0.1 * self.unitary_cost + self.lower_bound
            < other.cnot_cost + 0.1 * other.unitary_cost + other.lower_bound
        )

    def __ge__(self, other):
        return (
            self.cnot_cost + 0.1 * self.unitary_cost + self.lower_bound
            >= other.cnot_cost + 0.1 * other.unitary_cost + other.lower_bound
        )

    def __str__(self) -> str:
        return f"cnot_cost: {self.cnot_cost}, unitary_cost: {self.unitary_cost}, lower_bound: {self.lower_bound}"


def exact_cnot_synthesis(
    circuit: QCircuit,
    target_state: QState,
    optimality_level: int = 3,
    verbose_level: int = 0,
    runtime_limit: int = None,
):
    """This function finds the exact cnot_cnot_synthesis of a circuit .

    :param circuit: [description]
    :type circuit: QCircuit
    :param qubit_mapping: [description]
    :type qubit_mapping: dict
    :param target_state: [description]
    :type target_state: QState
    :param optimality_level: [description], defaults to 3
    :type optimality_level: int, optional
    :param verbose_level: [description], defaults to 0
    :type verbose_level: int, optional
    :raises ValueError: [description]
    :return: [description]
    :rtype: [type]
    """

    # now we start the search
    visited_states = set()
    state_queue = PriorityQueue()
    enquened_states = {}
    record = {}

    def map_qubit(qubit_index: int) -> int:
        return circuit.qubit_at(qubit_index)

    def explore_state(
        curr_state: QState, quantum_operator: QOperator, curr_cost: AStarCost
    ) -> QState:
        """Explore a state in a SRGraph ."""
        nonlocal visited_states, state_queue, enquened_states, record
        try:
            next_state = quantum_operator(curr_state)
        except ValueError:
            return None

        next_cost = AStarCost(
            curr_cost.cnot_cost + quantum_operator.get_cost(),
            curr_cost.unitary_cost + 1,
            next_state.get_lower_bound(),
        )

        next_state_repr = next_state.repr()

        # we skip the state if it is already visited
        if next_state_repr in visited_states:
            return None

        # we skip the state if it is already enquened and the cost is higher
        if (
            next_state_repr in enquened_states
            and next_cost >= enquened_states[next_state_repr]
        ):
            return None

        # now we add the state to the queue
        state_queue.put((next_cost, next_state))
        enquened_states[next_state_repr] = next_cost

        # we record the gate
        gate: QGate = None
        match quantum_operator.operator_type:
            case QOperatorType.X:
                gate = X(map_qubit(quantum_operator.target_qubit_index))
            case QOperatorType.CX:
                gate = CX(
                    map_qubit(quantum_operator.control_qubit_index),
                    quantum_operator.control_qubit_phase,
                    map_qubit(quantum_operator.target_qubit_index),
                )
            case QOperatorType.T0 | QOperatorType.T1:
                gate = MCRY(
                    quantum_operator.theta,
                    [],
                    [],
                    map_qubit(quantum_operator.target_qubit_index),
                )

            case QOperatorType.CT0 | QOperatorType.CT1:
                gate = MCRY(
                    quantum_operator.theta,
                    [map_qubit(quantum_operator.control_qubit_index)],
                    [quantum_operator.control_qubit_phase],
                    map_qubit(quantum_operator.target_qubit_index),
                )

        # and record the quantum_operator
        record[next_state] = curr_state, gate

        return next_state

    # begin of the exact synthesis algorithm
    num_qubits = target_state.num_qubits
    initial_state = QState.ground_state(num_qubits)

    curr_state = target_state
    curr_cost = AStarCost(0, 0, curr_state.get_lower_bound())
    state_queue.put((curr_cost, curr_state))

    solution_reached: bool = False

    sparsity = target_state.get_sparsity()
    best_supports = target_state.get_supports()

    start_time = time.time()

    # This function is called by the search loop.
    while not state_queue.empty():
        curr_cost, curr_state = state_queue.get()

        now_time = time.time()
        seconds_ellapsed = now_time - start_time
        if runtime_limit is not None and seconds_ellapsed > runtime_limit:
            break

        if curr_state == initial_state:
            # then we have found the solution
            solution_reached = True
            break

        _sparsity = curr_state.get_sparsity()
        _supports = curr_state.get_supports()

        num_supports = len(_supports)
        _optimality_level = optimality_level

        if _sparsity == 1:
            solution_reached = True
            break

        if _sparsity >= 2 and _sparsity < sparsity:
            sparsity = _sparsity
            if verbose_level >= 1:
                print(f"sparsity: {sparsity}")

            if _optimality_level <= 2:
                state_queue = PriorityQueue()
                enquened_states = {}

        if len(_supports) < len(best_supports):
            best_supports = _supports[:]
            if verbose_level >= 1:
                print(f"supports: {_supports}, length = {len(_supports)}")

            if _optimality_level <= 2:
                state_queue = PriorityQueue()
                enquened_states = {}

        curr_state_repr = curr_state.repr()
        visited_states.add(curr_state_repr)
        supports = curr_state.get_supports()

        search_done = False

        # try dependency analysis
        if not search_done:
            signatures = curr_state.get_qubit_signatures()
            const1 = curr_state.get_const1_signature()
            signature_to_qubits = {}
            for qubit_index, signature in enumerate(signatures):
                if signature == 0 or signature == const1:
                    continue
                if signature in signature_to_qubits:
                    quantum_operator = CXOperator(
                        qubit_index, signature_to_qubits[signature], True
                    )
                    next_state = explore_state(curr_state, quantum_operator, curr_cost)
                    search_done = True
                    break
                elif signature ^ const1 in signature_to_qubits:
                    quantum_operator = CXOperator(
                        qubit_index, signature_to_qubits[signature ^ const1], False
                    )
                    next_state = explore_state(curr_state, quantum_operator, curr_cost)
                    search_done = True
                    break
                else:
                    signature_to_qubits[signature] = qubit_index

            # try higher level dependency analysis
            if _optimality_level <= 2:
                for qubit_index1, signature1 in enumerate(signatures):
                    if signature1 == 0 or signature1 == const1:
                        continue
                    for qubit_index2, signature2 in enumerate(signatures):
                        if qubit_index1 == qubit_index2:
                            continue
                        if signature2 == 0 or signature2 == const1:
                            continue

                        if signature1 ^ signature2 in signature_to_qubits:
                            quantum_operator = CXOperator(
                                qubit_index1,
                                signature_to_qubits[signature1 ^ signature2],
                                True,
                            )
                            next_state = explore_state(
                                curr_state, quantum_operator, curr_cost
                            )
                            if next_state is not None:
                                quantum_operator = CXOperator(
                                    qubit_index2,
                                    signature_to_qubits[signature1 ^ signature2],
                                    True,
                                )
                                explore_state(next_state, quantum_operator, curr_cost)

                            search_done = True
                            break
                        elif signature1 ^ signature2 ^ const1 in signature_to_qubits:
                            quantum_operator = CXOperator(
                                qubit_index1,
                                signature_to_qubits[signature1 ^ signature2 ^ const1],
                                True,
                            )
                            next_state = explore_state(
                                curr_state, quantum_operator, curr_cost
                            )
                            if next_state is not None:
                                quantum_operator = CXOperator(
                                    qubit_index2,
                                    signature_to_qubits[
                                        signature1 ^ signature2 ^ const1
                                    ],
                                    False,
                                )
                                explore_state(next_state, quantum_operator, curr_cost)

                            search_done = True
                            break
                        else:
                            pass

        # apply merge0
        if not search_done:
            for target_qubit in supports:
                quantum_operator = TROperator(target_qubit, True)
                explore_state(curr_state, quantum_operator, curr_cost)
                quantum_operator = TROperator(target_qubit, False)
                next_state = explore_state(curr_state, quantum_operator, curr_cost)
                if _optimality_level <= 3 and next_state is not None:
                    search_done = True
                    break

        # apply cmerge
        if not search_done:
            for target_qubit in supports:
                if search_done:
                    break
                for control_qubit in supports:
                    if control_qubit == target_qubit:
                        continue
                    if search_done:
                        break
                    for phase in [True, False]:
                        if search_done:
                            break
                        for target_phase in [True, False]:
                            quantum_operator = CTROperator(
                                target_qubit, target_phase, control_qubit, phase
                            )
                            next_state = explore_state(
                                curr_state, quantum_operator, curr_cost
                            )
                            if _optimality_level <= 1 and next_state is not None:
                                if (
                                    next_state.get_sparsity()
                                    <= curr_state.get_sparsity() - 1
                                ):
                                    search_done = True
                                    break

        # CNOT
        if not search_done:
            for target_qubit in supports:
                if search_done:
                    break
                for control_qubit in supports:
                    if control_qubit == target_qubit:
                        continue
                    if search_done:
                        break
                    for phase in [True, False]:
                        quantum_operator = CXOperator(
                            target_qubit, control_qubit, phase
                        )
                        next_state = explore_state(
                            curr_state, quantum_operator, curr_cost
                        )

        # apply x
        if not search_done:
            if _optimality_level <= 3 and curr_state.get_sparsity() != 1:
                pass
            else:
                for target_qubit in supports:
                    quantum_operator = XOperator(target_qubit)
                    explore_state(curr_state, quantum_operator, curr_cost)

    if not solution_reached:
        raise ValueError("No solution found")

    final_state = QState(curr_state.index_to_weight, curr_state.num_qubits)

    x_gates = ground_state_calibration(circuit, final_state)

    gates = x_gates[:]
    while curr_state in record:
        prev_state, gate = record[curr_state]
        gates.append(gate)
        curr_state = prev_state
        if verbose_level >= 1:
            print(f"curr_state: {curr_state}")

    return gates
