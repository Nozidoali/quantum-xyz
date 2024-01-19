#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

import numpy as np
import copy

from queue import PriorityQueue

import xyz.qstate as qs
import xyz.operator as op
import xyz.circuit as qc

from ._ground_state_calibration import ground_state_calibration

DEPRECATED: bool = True

def exact_cnot_synthesis_legacy(
    circuit: qc.QCircuit,
    target_state: qs.QState,
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

    # we should raise an error, since this is the old version
    if DEPRECATED:
        raise ValueError(
            "This is the old version of exact_cnot_synthesis, please use the new version"
        )

    # now we start the search
    visited_states = set()
    state_queue = PriorityQueue()
    enquened_states = {}
    record = {}

    def explore_state(
        curr_state: qs.QState, gates: op.QOperator, curr_cost: int
    ) -> qs.QState:
        """Explore a state in a SRGraph ."""
        nonlocal visited_states, state_queue, enquened_states, record, circuit

        next_state = copy.deepcopy(curr_state)
        gate_cost = 0
        for gate in gates:
            try:
                match gate.qgate_type:
                    case qc.QGateType.X:
                        gate: qc.X
                        next_state = next_state.apply_x(gate.target_qubit.index)
                        gate_cost += 0.05
                    case qc.QGateType.CX:
                        gate: qc.CX
                        next_state = next_state.apply_cx(
                            gate.control_qubit.index,
                            gate.phase,
                            gate.target_qubit.index,
                        )
                        gate_cost += 1
                    case qc.QGateType.RY:
                        gate: qc.RY
                        next_state = next_state.apply_ry(
                            gate.target_qubit.index, -gate.theta
                        )
                        gate_cost += 0.05
                    case _:
                        raise ValueError(f"Unknown gate type: {gate.qgate_type}")

                if verbose_level >= 3:
                    print(
                        f"next_state: {next_state}, curr_state = {curr_state} gate = {gate}"
                    )
            except ValueError:
                return None

        next_cost = curr_cost + gate_cost
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

        # and record the quantum_operator
        if verbose_level >= 3:
            print(
                f"recording [{hash(next_state)}] <- {hash(curr_state)}, gate: {gates}"
            )
        record[hash(next_state)] = hash(curr_state), gates[::-1]

        return next_state

    # begin of the exact synthesis algorithm
    num_qubits = target_state.num_qubits
    initial_state = qs.QState.ground_state(num_qubits)

    curr_state = target_state
    curr_cost = 0
    state_queue.put((curr_cost, curr_state))

    solution_reached: bool = False

    while not state_queue.empty():
        curr_cost, curr_state = state_queue.get()

        if verbose_level == 1:
            print(
                f"#visited: {len(visited_states)} #enquened: {state_queue.qsize()}, #cost: {curr_cost}\r",
                end="",
            )

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

        if _sparsity == 1:
            solution_reached = True
            break

        curr_state_repr = curr_state.repr()
        visited_states.add(curr_state_repr)
        supports = curr_state.get_supports()

        for target_qubit in supports:
            # X
            explore_state(curr_state, [qc.X(circuit.qubit_at(target_qubit))], curr_cost)

            thetas = curr_state.get_ry_angles(target_qubit)
            if verbose_level >= 3:
                print(f"thetas: {thetas}")

            # RY
            # find the most frequent theta
            # best_theta = curr_state.get_most_frequent_theta(target_qubit)

            # if best_theta is not None and not np.isclose(best_theta, 0):
            for theta in sorted(thetas):
                explore_state(
                    curr_state,
                    [qc.RY(theta, circuit.qubit_at(target_qubit))],
                    curr_cost,
                )
                continue

            # CX
            for control_qubit in supports:
                if control_qubit != target_qubit:
                    cry_thetas = curr_state.get_cry_angles(control_qubit, target_qubit)

                    prev_theta = None
                    for theta in sorted(cry_thetas):
                        if prev_theta is not None and np.isclose(theta, prev_theta):
                            continue
                        if verbose_level >= 3:
                            print(f"cry theta: {theta}")
                        explore_state(
                            curr_state,
                            [
                                qc.RY(theta, circuit.qubit_at(target_qubit)),
                                qc.CX(
                                    circuit.qubit_at(control_qubit),
                                    0,
                                    circuit.qubit_at(target_qubit),
                                ),
                                qc.RY(-theta, circuit.qubit_at(target_qubit)),
                            ],
                            curr_cost,
                        )
                        explore_state(
                            curr_state,
                            [
                                qc.RY(theta, circuit.qubit_at(target_qubit)),
                                qc.CX(
                                    circuit.qubit_at(control_qubit),
                                    1,
                                    circuit.qubit_at(target_qubit),
                                ),
                                qc.RY(-theta, circuit.qubit_at(target_qubit)),
                            ],
                            curr_cost,
                        )
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
        prev_hash, _gates = record[curr_hash]
        for _gate in _gates:
            gates.append(_gate)
        curr_hash = prev_hash
        if verbose_level >= 1:
            print(f"curr_hash: {curr_hash}, gate: {gate}")

    return gates
