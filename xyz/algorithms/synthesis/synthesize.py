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

from xyz.srgraph import (
    QState,
    SRGraph,
    MCRYOperator,
    QOperatorType,
    QuantizedRotationType,
    QOperator,
    quantize_state,
    lookup_repr,
)

from xyz.circuit import QCircuit, X, MCRY, MULTIPLEXY


def synthesize(state_vector: np.ndarray, verbose_level: int = 0) -> SRGraph:
    """
    @brief Runs the search based state synthesis
    @param verbose_level Whether to print out the state of the search
    """

    target_state = quantize_state(state_vector)

    srg = SRGraph(target_state.num_qubits)

    weights = state_vector[:]

    visited_states = set()
    state_queue = PriorityQueue()
    enquened_states = {}
    record = {}

    def explore_state(
        srg: SRGraph, curr_state: QState, quantum_operator: QOperator, curr_cost: int
    ) -> None:
        """Explore a state in a SRGraph .
        """
        nonlocal visited_states, state_queue, enquened_states, record
        next_state = quantum_operator(curr_state)
        next_cost = (
            curr_cost
            + quantum_operator.get_cost()
            + next_state.get_lower_bound()
            - curr_state.get_lower_bound()
        )

        state = lookup_repr(next_state)

        # we skip the state if it is already visited
        if state in visited_states:
            return

        # we skip the state if it is already enquened and the cost is higher
        if state in enquened_states and next_cost >= enquened_states[state]:
            return

        # now we add the state to the queue
        state_queue.put((next_cost, next_state))
        enquened_states[state] = next_cost

        # and record the quantum_operator
        record[next_state] = curr_state, quantum_operator

    curr_state = copy.deepcopy(target_state)
    curr_cost = curr_state.get_lower_bound()
    state_queue.put((curr_cost, curr_state))
    enquened_states[curr_state] = curr_cost

    solution_reached: bool = False
    
    # This function is called by the search loop.
    while not state_queue.empty():
        curr_cost, curr_state = state_queue.get()

        canonical_state = lookup_repr(curr_state)
        visited_states.add(canonical_state)

        if len(canonical_state) == 0:
            # then we have found the solution
            solution_reached = True
            break

        for target_qubit in range(srg.num_qubits):
            pos_cofactor, neg_cofactor = curr_state.cofactors(target_qubit)

            # skip if the target qubit is already 1
            if curr_state.patterns[target_qubit] == 0:
                continue

            for control_qubit in range(srg.num_qubits):
                if control_qubit == target_qubit:
                    continue

                if curr_state.patterns[control_qubit] == 0:
                    continue

                for phase in [True, False]:
                    pos_cofactor, neg_cofactor = curr_state.controlled_cofactors(
                        target_qubit, control_qubit, phase
                    )

                    if len(pos_cofactor) > 0 and pos_cofactor == neg_cofactor:
                        # apply merge0
                        quantum_operator = MCRYOperator(
                            target_qubit,
                            QuantizedRotationType.MERGE0,
                            [control_qubit],
                            [phase],
                        )
                        explore_state(srg, curr_state, quantum_operator, curr_cost)

                        # apply merge1
                        quantum_operator = MCRYOperator(
                            target_qubit,
                            QuantizedRotationType.MERGE1,
                            [control_qubit],
                            [phase],
                        )
                        explore_state(srg, curr_state, quantum_operator, curr_cost)

                # CNOT
                for phase in [True]:
                    quantum_operator = MCRYOperator(
                        target_qubit,
                        QuantizedRotationType.SWAP,
                        [control_qubit],
                        [phase],
                    )
                    explore_state(srg, curr_state, quantum_operator, curr_cost)

    assert solution_reached
    # assert QState.ground_state(srg.num_qubits) in record
    curr_basis = curr_state.to_index_set()
    print('\n'.join([f"{i:0{srg.num_qubits}b}: {weights[i]}" for i in curr_basis]))

    state_tranformations = []
    while curr_state in record:
        prev_state, quantum_operator = record[curr_state]

        state_before = prev_state.to_index_set()
        state_after = curr_state.to_index_set()
        state_tranformations.append((state_before, quantum_operator, state_after))
        curr_state = prev_state

    # initialize the circuit
    circuit = QCircuit(srg.num_qubits)
    gates = []
    
    
    for state_before, quantum_operator, state_after in reversed(state_tranformations):
        
        if verbose_level == 2:
            state_before_str = "\n".join([f"{i:0{circuit.get_num_qubits()}b} {weights[i]}" for i in state_before])
            print(f"quantum_operator: {quantum_operator}")
            print(f"state_before: \n{state_before_str}")
            print(weights)
        
        if quantum_operator.operator_type == QOperatorType.X:
            gate = X(circuit.qubit_at(quantum_operator.target_qubit_index))
            gates.append(gate)

        else:
            new_weights = np.zeros(1 << srg.num_qubits)

            control_qubits = [
                circuit.qubit_at(i) for i in quantum_operator.control_qubit_indices
            ]
            phases = quantum_operator.control_qubit_phases
            target_qubit = circuit.qubit_at(quantum_operator.target_qubit_index)

            # CX or X
            if quantum_operator.rotation_type == QuantizedRotationType.SWAP:
                for idx in state_before:
                    ridx = idx ^ (1 << quantum_operator.target_qubit_index)
                    if not quantum_operator.is_controlled(idx):
                        # if the state is controlled, we need to check if the control qubits are all 1
                        new_weights[idx] += weights[idx]
                        weights[idx] = 0
                    else:
                        new_weights[ridx] += weights[idx]
                        weights[idx] = 0
                gate = MCRY(np.pi, control_qubits, phases, target_qubit)
                gates.append(gate)

            # U(2)
            else:
                thetas = {}
                for idx in state_before:
                    ridx = idx ^ (1 << quantum_operator.target_qubit_index)
                    if not quantum_operator.is_controlled(idx):
                        new_weights[idx] += weights[idx]
                        weights[idx] = 0
                    else:
                        if weights[idx] + weights[ridx] == 0:
                            continue

                        theta = 2 * np.arccos(
                            np.sqrt(weights[idx] / (weights[idx] + weights[ridx]))
                        )
                        thetas[theta] = idx
                        new_weights[idx] += weights[idx] + weights[ridx]
                        weights[idx] = 0
                        weights[ridx] = 0
                if len(thetas) == 0:
                    assert False, "No theta found"

                elif len(thetas) == 1:
                    theta = list(thetas.keys())[0]
                    gate = MCRY(theta, control_qubits, phases, target_qubit)
                    gates.append(gate)

                else:
                    if len(thetas) == 2:

                        state1, state2, *_ = list(thetas.values())

                        # find the first different bit, use it as the decision variable
                        decision_variable: int = (state1 ^ state2).bit_length() - 1

                        phase1 = (int(state1) >> decision_variable) & 1
                        phase2 = (int(state2) >> decision_variable) & 1

                        control_qubits.append(circuit.qubit_at(decision_variable))

                        phases1 = phases + [phase1]
                        phases2 = phases + [phase2]

                        theta1 = list(thetas.keys())[0]
                        theta2 = list(thetas.keys())[1]
                        
                        print(f"theta1: {theta1}, theta2: {theta2}")

                        if len(control_qubits) == 1:
                            # special case
                            gate = MULTIPLEXY(
                                theta1, theta2, control_qubits[0], target_qubit
                            )
                            gates.append(gate)

                        else:
                            gate1 = MCRY(theta1, control_qubits, phases1, target_qubit)
                            gate2 = MCRY(theta2, control_qubits, phases2, target_qubit)
                            gates.append(gate1)
                            gates.append(gate2)
                    else:
                        raise NotImplementedError
        weights = new_weights[:] # copy
        if verbose_level == 2:
            state_after_str = "\n".join([f"{i:0{circuit.get_num_qubits()}b}: {weights[i]}" for i in state_after])
            print(f"state_after: \n{state_after_str}")
            print(weights)

    for gate in gates[::-1]:
        print(gate)
        circuit.add_gate(gate)

    return circuit
