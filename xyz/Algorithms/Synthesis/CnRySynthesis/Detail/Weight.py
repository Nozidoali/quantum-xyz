#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 18:10:34
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 18:35:02
"""

import numpy as np

from typing import List
from .CnRyMove import *
from xyz.circuit import *


class WeightTracer:
    def __init__(self, num_qubits: int, initial_state: List[int]) -> None:
        self.num_qubits = num_qubits
        self.weights = np.zeros(1 << num_qubits)
        self.mrcy_gates = []
        self.circuit = QCircuit(num_qubits)
        self.circuit.set_mapping(False)

        for state in initial_state:
            self.weights[state] = 1

    def trace(self, move_from_state: List[int], move: CnRyMove) -> None:
        logging.debug(f"weight before merge: {self.weights}")

        new_weights = np.zeros(1 << self.num_qubits)

        control_qubits = [self.circuit.qubit_at(i) for i, _ in move.control_states]
        phases = [phase for _, phase in move.control_states]
        target_qubit = self.circuit.qubit_at(move.pivot_qubit)

        # this is the case of swap
        if move.direction == CnRYDirection.SWAP:
            for i in move_from_state:
                if (
                    move.control_state is not None
                    and (move.control_state >> i) & 1 == 0
                ):
                    new_weights[i] += self.weights[i]
                    self.weights[i] = 0
                    continue
                new_weights[i] += self.weights[i ^ (1 << move.pivot_qubit)]
                self.weights[i ^ (1 << move.pivot_qubit)] = 0

            self.weights = new_weights

            gate = MCRY(-np.pi, control_qubits, phases, target_qubit)
            self.mrcy_gates.append(gate)

        # this is the case of merge
        else:
            thetas = {}

            for i in move_from_state:
                if (
                    move.control_state is not None
                    and (move.control_state >> i) & 1 == 0
                ):
                    new_weights[i] += self.weights[i]
                    self.weights[i] = 0
                    continue

                if self.weights[i] + self.weights[i ^ (1 << move.pivot_qubit)] == 0:
                    continue

                theta = 2 * np.arccos(
                    np.sqrt(
                        self.weights[i]
                        / (self.weights[i] + self.weights[i ^ (1 << move.pivot_qubit)])
                    )
                )
                thetas[theta] = i

                new_weights[i] += (
                    self.weights[i] + self.weights[i ^ (1 << move.pivot_qubit)]
                )
                self.weights[i] = 0
                self.weights[i ^ (1 << move.pivot_qubit)] = 0

            self.weights = new_weights

            if len(thetas) == 0:
                assert False, "No theta found"

            elif len(thetas) == 1:
                theta = list(thetas.keys())[0]
                gate = MCRY(theta, control_qubits, phases, target_qubit)
                self.mrcy_gates.append(gate)

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
                        self.mcry_gates.append(gate)

                    else:
                        gate1 = MCRY(theta1, control_qubits, phases1, target_qubit)
                        gate2 = MCRY(theta2, control_qubits, phases2, target_qubit)
                        self.mcry_gates.append(gate1)
                        self.mcry_gates.append(gate2)
                else:
                    raise NotImplementedError

        logging.debug(f"weight after merge: {self.weights}")

    def export(self) -> QCircuit:
        for gate in self.mrcy_gates[::-1]:
            self.circuit.add_gate(gate)
        self.circuit.flush()
        self.circuit.measure()
        return self.circuit
