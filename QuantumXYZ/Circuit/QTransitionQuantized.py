#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 16:33:40
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 19:48:47
'''

from .Operators import *
from .QTransitionBase import *
from .QCircuit import *

from typing import List

class QTransitionQuantized(QTransitionBase):
    
    def __init__(self, num_qubits: int) -> None:
        QTransitionBase.__init__(self, num_qubits)

    def recover_circuit(self, _weights: List[float]) -> QCircuit:

        circuit = QCircuit(self.num_qubits)

        # first we assign the weights to the last state
        weights = _weights[:] # copy

        num_transitions = self.num_transitions()

        gates = []
        
        for i in range(num_transitions, 0, -1):
            operator: MCRYOperator
            state_before, operator, state_after = self.transition_at(i - 1)

            if operator.type == QOperatorType.X:
                gate = X(circuit.qubit_at(operator.target_qubit_index))
            
            else:
                new_weights = np.zeros(1 << self.num_qubits)

                control_qubits = [circuit.qubit_at(i) for i in operator.control_qubit_indices]
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
                    
                    gate = MCRY(-np.pi, control_qubits, phases, target_qubit)

                    gates.append(gate)

                else:
                    thetas = {}

                    print(f"state_before: {state_before}, state_after: {state_after}")

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
                                np.sqrt(
                                    weights[idx]
                                    / (weights[idx] + weights[ridx])
                                )
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
                            state1, state2 = list(thetas.values())

                            decision_variable: int = int(np.floor(np.log2(state1 ^ state2)))

                            phase1 = (int(state1) >> decision_variable) & 1
                            phase2 = (int(state2) >> decision_variable) & 1

                            control_qubits.append(self.circuit.qubit_at(decision_variable))

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