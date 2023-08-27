#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""


import copy
from queue import PriorityQueue
import numpy as np
from sympy import true
from xyz.circuit.basic_gates.base.gate import QGate
from xyz.circuit.basic_gates.cx import CX

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

from xyz.circuit import QCircuit, X, MCRY


def synthesize(
    state_vector: np.ndarray, optimality_level: int = 3, verbose_level: int = 0
) -> SRGraph:
    """
    @brief Runs the search based state synthesis
    @param verbose_level Whether to print out the state of the search
    """

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

    target_state = quantize_state(state_vector)
    num_qubits = target_state.num_qubits
    initial_state = QState.ground_state(num_qubits)

    # initialize the circuit
    circuit = QCircuit(num_qubits)

    visited_states = set()
    state_queue = PriorityQueue()
    enquened_states = {}
    record = {}

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
        if next_state_repr in enquened_states and next_cost >= enquened_states[next_state_repr]:
            return None

        # now we add the state to the queue
        state_queue.put((next_cost, next_state))
        enquened_states[next_state_repr] = next_cost

        # we record the gate
        gate: QGate = None
        match quantum_operator.operator_type:
            case QOperatorType.X:
                gate = X(circuit.qubit_at(quantum_operator.target_qubit_index))
            case QOperatorType.CX:
                gate = CX(
                    circuit.qubit_at(quantum_operator.control_qubit_index),
                    quantum_operator.control_qubit_phase,
                    circuit.qubit_at(quantum_operator.target_qubit_index),
                )
            case QOperatorType.T0 | QOperatorType.T1:
                gate = MCRY(
                    quantum_operator.theta,
                    [],
                    [],
                    circuit.qubit_at(quantum_operator.target_qubit_index),
                )

            case QOperatorType.CT0 | QOperatorType.CT1:
                gate = MCRY(
                    quantum_operator.theta,
                    [circuit.qubit_at(quantum_operator.control_qubit_index)],
                    [quantum_operator.control_qubit_phase],
                    circuit.qubit_at(quantum_operator.target_qubit_index),
                )

        # and record the quantum_operator
        record[next_state] = curr_state, gate

        return next_state

    curr_state = target_state
    curr_cost = AStarCost(0, 0, curr_state.get_lower_bound())
    state_queue.put((curr_cost, curr_state))

    solution_reached: bool = False

    sparsity = target_state.get_sparsity()
    supports = target_state.get_supports()

    # This function is called by the search loop.
    while not state_queue.empty():
        curr_cost, curr_state = state_queue.get()

        # print(f"curr_state: {curr_state}, curr_cost: {curr_cost}")

        if curr_state == initial_state:
            # then we have found the solution
            solution_reached = True
            break

        _sparsity = curr_state.get_sparsity()
        if _sparsity >= 2 and _sparsity < sparsity:
            sparsity = _sparsity
            print(f"sparsity: {sparsity}")

            if optimality_level <= 2:
                state_queue = PriorityQueue()
                enquened_states = {}

        _supports = curr_state.get_supports()
        if len(_supports) < len(supports):
            supports = _supports
            print(f"supports: {supports}")

            if optimality_level <= 1:
                state_queue = PriorityQueue()
                enquened_states = {}

        curr_state_repr = curr_state.repr()
        visited_states.add(curr_state_repr)
        supports = curr_state.get_supports()

        search_done = False

        # apply merge0
        if not search_done:
            for target_qubit in supports:
                quantum_operator = TROperator(target_qubit, True)
                explore_state(curr_state, quantum_operator, curr_cost)
                quantum_operator = TROperator(target_qubit, False)
                next_state = explore_state(curr_state, quantum_operator, curr_cost)
                if optimality_level <= 2 and next_state is not None:
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
                            if optimality_level <= 1 and next_state is not None:
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
                        if optimality_level <= 1:
                            if (
                                next_state is not None
                                and next_state.get_supports()
                                < curr_state.get_supports()
                            ):
                                search_done = True
                                break

        # apply x
        if not search_done:
            if optimality_level <= 2 and curr_state.get_sparsity() != 1:
                pass
            else:
                for target_qubit in supports:
                    quantum_operator = XOperator(target_qubit)
                    explore_state(curr_state, quantum_operator, curr_cost)

    assert solution_reached

    while curr_state in record:
        prev_state, gate = record[curr_state]
        circuit.add_gate(gate)
        curr_state = prev_state
        print(f"curr_state: {curr_state}")
    return circuit
