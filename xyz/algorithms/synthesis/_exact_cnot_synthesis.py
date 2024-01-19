#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

from queue import PriorityQueue
from xyz.circuit.basic_gates.base.gate import QGate
from xyz.circuit.basic_gates.cx import CX
from xyz.circuit import QCircuit, X, MCRY

import xyz.qstate as qs
import xyz.operator as op

from ._ground_state_calibration import ground_state_calibration


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
    target_state: qs.QState,
    optimality_level: int = 3,
    verbose_level: int = 0,
    cnot_limit: int = None,
):
    """This function finds the exact cnot_cnot_synthesis of a circuit .

    :param circuit: [description]
    :type circuit: QCircuit
    :param qubit_mapping: [description]
    :type qubit_mapping: dict
    :param target_state: [description]
    :type target_state: qs.QState
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
        curr_state: qs.QState, quantum_operator: op.QOperator, curr_cost: AStarCost
    ) -> qs.QState:
        """Explore a state in a SRGraph ."""
        nonlocal visited_states, state_queue, enquened_states, record
        try:
            next_state = quantum_operator(curr_state)
            if verbose_level >= 3:
                print(
                    f"next_state: {next_state}, curr_state = {curr_state} gate = {quantum_operator}"
                )
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
        gate_to_record: QGate = None
        match quantum_operator.operator_type:
            case op.QOperatorType.X:
                gate_to_record = X(map_qubit(quantum_operator.target_qubit_index))
            case op.QOperatorType.CX:
                gate_to_record = CX(
                    map_qubit(quantum_operator.control_qubit_index),
                    quantum_operator.control_qubit_phase,
                    map_qubit(quantum_operator.target_qubit_index),
                )
            case op.QOperatorType.T0 | op.QOperatorType.T1:
                gate_to_record = MCRY(
                    quantum_operator.theta,
                    [],
                    [],
                    map_qubit(quantum_operator.target_qubit_index),
                )

            case op.QOperatorType.CT0 | op.QOperatorType.CT1:
                gate_to_record = MCRY(
                    quantum_operator.theta,
                    [map_qubit(quantum_operator.control_qubit_index)],
                    [quantum_operator.control_qubit_phase],
                    map_qubit(quantum_operator.target_qubit_index),
                )

        # and record the quantum_operator
        if verbose_level >= 3:
            print(
                f"recording [{hash(next_state)}] <- {hash(curr_state)}, gate: {gate_to_record}"
            )
        record[hash(next_state)] = hash(curr_state), gate_to_record

        return next_state

    # begin of the exact synthesis algorithm
    num_qubits = target_state.num_qubits
    initial_state = qs.QState.ground_state(num_qubits)

    curr_state = target_state
    curr_cost = AStarCost(0, 0, curr_state.get_lower_bound())
    state_queue.put((curr_cost, curr_state))

    solution_reached: bool = False

    sparsity = target_state.get_sparsity()
    best_supports = target_state.get_supports()

    # This function is called by the search loop.
    while not state_queue.empty():
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

        _sparsity = curr_state.get_sparsity()
        _supports = curr_state.get_supports()

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
                    quantum_operator = op.CXOperator(
                        qubit_index, signature_to_qubits[signature], True
                    )
                    next_state = explore_state(curr_state, quantum_operator, curr_cost)
                    search_done = True
                    break
                elif signature ^ const1 in signature_to_qubits:
                    quantum_operator = op.CXOperator(
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
                            quantum_operator = op.CXOperator(
                                qubit_index1,
                                signature_to_qubits[signature1 ^ signature2],
                                True,
                            )
                            next_state = explore_state(
                                curr_state, quantum_operator, curr_cost
                            )
                            if next_state is not None:
                                quantum_operator = op.CXOperator(
                                    qubit_index2,
                                    signature_to_qubits[signature1 ^ signature2],
                                    True,
                                )
                                explore_state(next_state, quantum_operator, curr_cost)

                            search_done = True
                            break

                        elif signature1 ^ signature2 ^ const1 in signature_to_qubits:
                            quantum_operator = op.CXOperator(
                                qubit_index1,
                                signature_to_qubits[signature1 ^ signature2 ^ const1],
                                True,
                            )
                            next_state = explore_state(
                                curr_state, quantum_operator, curr_cost
                            )
                            if next_state is not None:
                                quantum_operator = op.CXOperator(
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
                quantum_operator = op.TROperator(target_qubit, True)
                explore_state(curr_state, quantum_operator, curr_cost)
                quantum_operator = op.TROperator(target_qubit, False)
                explore_state(curr_state, quantum_operator, curr_cost)

        # apply cmerge
        if not search_done:
            for target_qubit in supports:
                for control_qubit in supports:
                    if control_qubit == target_qubit:
                        continue
                    for phase in [True, False]:
                        for target_phase in [True, False]:
                            quantum_operator = op.CTROperator(
                                target_qubit, target_phase, control_qubit, phase
                            )
                            explore_state(curr_state, quantum_operator, curr_cost)

        # CNOT
        if not search_done:
            for target_qubit in supports:
                for control_qubit in supports:
                    if control_qubit == target_qubit:
                        continue
                    for phase in [True, False]:
                        quantum_operator = op.CXOperator(
                            target_qubit, control_qubit, phase
                        )
                        explore_state(curr_state, quantum_operator, curr_cost)

        # apply x
        if not search_done:
            if _optimality_level <= 3 and curr_state.get_sparsity() != 1:
                # we can prove that we only need to apply X once, so we skip the rest
                pass
            else:
                for target_qubit in supports:
                    quantum_operator = op.XOperator(target_qubit)
                    explore_state(curr_state, quantum_operator, curr_cost)

    if not solution_reached:
        raise ValueError("No solution found")

    final_state = qs.QState(curr_state.index_to_weight, curr_state.num_qubits)

    x_gates = ground_state_calibration(circuit, final_state)

    if verbose_level >= 2:
        print("\n\n")

    for record_key, record_value in record.items():
        prev_state, gate = record_value
        if verbose_level >= 2:
            print(
                f"record_key: {record_key}\n\t prev_state: {prev_state}\n\t gate: {gate}"
            )

    gates = x_gates[:]
    backtraced_states: set = set()
    curr_hash = hash(curr_state)
    while curr_hash in record:
        if curr_hash in backtraced_states:
            raise ValueError("Loop found")
        backtraced_states.add(curr_hash)
        prev_hash, gate = record[curr_hash]
        gates.append(gate)
        curr_hash = prev_hash
        if verbose_level >= 2:
            print(f"curr_hash: {curr_hash:0b}, gate: {gate}")

    return gates
