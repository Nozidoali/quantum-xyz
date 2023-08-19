#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 16:33:40
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 20:05:52
"""

from typing import List
import numpy as np

from xyz.circuit import QCircuit, X, MCRY, MULTIPLEXY
from xyz.srgraph import MCRYOperator, QOperatorType, QuantizedRotationType


def convert_srg_to_circuit(
    transitions, _weights: List[float], verbose: bool = False
) -> QCircuit:
    """Recover the circuit with the same weight and weights .

    :param _weights: [description]
    :type _weights: List[float]
    :param verbose: [description], defaults to False
    :type verbose: bool, optional
    :raises NotImplementedError: [description]
    :return: [description]
    :rtype: QCircuit
    """
    circuit = QCircuit(transitions.num_qubits)

    # first we assign the weights to the last state
    weights = _weights[:]  # copy

    num_transitions = transitions.num_transitions()

    gates = []

    for i in range(num_transitions, 0, -1):
        operator: MCRYOperator
        state_before, operator, state_after = transitions.transition_at(i - 1)

        if operator.operator_type == QOperatorType.X:
            gate = X(circuit.qubit_at(operator.target_qubit_index))
            gates.append(gate)

        else:
            new_weights = np.zeros(1 << transitions.num_qubits)

            control_qubits = [
                circuit.qubit_at(i) for i in operator.control_qubit_indices
            ]
            phases = operator.control_qubit_phases
            target_qubit = circuit.qubit_at(operator.target_qubit_index)

            if operator.rotation_type == QuantizedRotationType.SWAP:
                for pure_state in state_before:
                    idx = int(pure_state)
                    ridx = int(pure_state.flip(operator.target_qubit_index))
                    if not operator.is_controlled(idx):
                        # if the state is controlled, we need to check if the control qubits are all 1
                        new_weights[idx] += weights[idx]

                        weights[idx] = 0

                    else:
                        new_weights[idx] += weights[ridx]
                        weights[ridx] = 0

                weights = new_weights

                gate = MCRY(np.pi, control_qubits, phases, target_qubit)

                gates.append(gate)

            else:
                thetas = {}

                if verbose:
                    print(
                        f"state_before: \n{state_before}\n, state_after: \n{state_after}\n"
                    )

                pure_state: PureState
                for pure_state in state_before:
                    idx = int(pure_state)
                    ridx = int(pure_state.flip(operator.target_qubit_index))
                    if not operator.is_controlled(pure_state):
                        new_weights[idx] += weights[idx]
                        weights[idx] = 0
                    else:
                        if weights[idx] + weights[ridx] == 0:
                            continue

                        theta = 2 * np.arccos(
                            np.sqrt(weights[idx] / (weights[idx] + weights[ridx]))
                        )
                        thetas[theta] = pure_state

                        new_weights[idx] += weights[idx] + weights[ridx]

                        weights[idx] = 0
                        weights[ridx] = 0

                weights = new_weights

                if len(thetas) == 0:
                    assert False, "No theta found"

                elif len(thetas) == 1:
                    theta = list(thetas.keys())[0]
                    gate = MCRY(theta, control_qubits, phases, target_qubit)
                    gates.append(gate)

                else:
                    if len(thetas) == 2:
                        state1, state2, *_ = list(thetas.values())

                        decision_variable: int = find_first_diff_qubit_index(
                            state1, state2
                        )

                        phase1 = (int(state1) >> decision_variable) & 1
                        phase2 = (int(state2) >> decision_variable) & 1

                        control_qubits.append(circuit.qubit_at(decision_variable))

                        phases1 = phases + [phase1]
                        phases2 = phases + [phase2]

                        theta1 = list(thetas.keys())[0]
                        theta2 = list(thetas.keys())[1]

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

    for gate in gates[::-1]:
        print(gate)
        circuit.add_gate(gate)
    return circuit
