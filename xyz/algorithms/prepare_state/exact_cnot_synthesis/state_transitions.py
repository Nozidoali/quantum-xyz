#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-11 10:47:24
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-11 11:11:21
"""

import numpy as np

from xyz.circuit import QCircuit, QState, CX, CRY
from ..support_reduction import support_reduction
from ..rotation_angles import get_ap_cry_angles

APPLY_HEURISTIC = True


def get_state_transitions(circuit: QCircuit, curr_state: QState, supports: list = None):
    if supports is None:
        supports = curr_state.get_supports()

    # try dependency analysis
    new_state, gates = support_reduction(circuit, curr_state)
    if len(gates) > 0:
        return [[new_state, gates]]

    # apply CRY
    transitions = []
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
                transitions.append(
                    [
                        None,
                        [
                            CRY(
                                cry_angle,
                                circuit.qubit_at(control_qubit),
                                phase,
                                circuit.qubit_at(target_qubit),
                            )
                        ],
                    ]
                )

                if not APPLY_HEURISTIC:
                    transitions.append(
                        [
                            None,
                            [
                                CRY(
                                    cry_angle - np.pi,
                                    circuit.qubit_at(control_qubit),
                                    phase,
                                    circuit.qubit_at(target_qubit),
                                )
                            ],
                        ]
                    )

        # apply CNOT
        for target_qubit in supports:
            for control_qubit in supports:
                if control_qubit == target_qubit:
                    continue
                # for phase in [True, False]:
                if APPLY_HEURISTIC:
                    for phase in [True]:
                        gate = CX(
                            circuit.qubit_at(control_qubit),
                            phase,
                            circuit.qubit_at(target_qubit),
                        )
                        transitions.append([None, [gate]])

    return transitions
