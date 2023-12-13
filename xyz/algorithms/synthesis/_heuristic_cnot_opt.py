#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:51:03
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 12:56:17
"""

import copy
from collections import Counter

import xyz.qstate as qs
import xyz.circuit as qc


def heurisitc_cnot_synthesis_opt(
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

    curr_state = copy.deepcopy(target_state)

    if verbose_level >= 3:
        print(f"preparing the target state {target_state} ...")

    gates = []

    while curr_state != qs.QState.ground_state(target_state.num_qubits):
        print(f"\t\tcurrent state: {curr_state}")

        supports = curr_state.get_supports()

        # we decide the best qubit to be the target qubit
        best_qubit_index: int = None
        best_control_qubit_index: int = None
        best_cry_theta: float = None
        best_ry_theta: float = None
        best_score: int = 0

        for qubit_index in supports:
            thetas = curr_state.get_ry_angles(qubit_index)

            # we calculate the RY score
            # print(f"qubit {qubit_index}: {thetas}")
            initial_score = len(thetas) - thetas.count(0)
            # print(f"initial score: {initial_score}, state = {rotated_state}")

            # let us first try to apply the RY gate
            most_frequent_theta, frequency = Counter(thetas).most_common(1)[0]
            print(f"most frequent theta: {most_frequent_theta}, frequency: {frequency}")
            if most_frequent_theta != 0 and frequency > thetas.count(0):
                # then we apply and return
                curr_state = curr_state.apply_ry(qubit_index, -most_frequent_theta)
                gates.append(qc.RY(most_frequent_theta, circuit.qubit_at(qubit_index)))
                break

            print(f"\n\nstate before: {curr_state} score {initial_score}")

            for control_qubit_index in supports:
                if control_qubit_index == qubit_index:
                    continue

                cry_thetas = curr_state.get_cry_angles(control_qubit_index, qubit_index)

                for cry_theta in cry_thetas:
                    candidate_state: qs.QState
                    candidate_state = curr_state.apply_ry(qubit_index, cry_theta)
                    candidate_state = candidate_state.apply_cx(
                        control_qubit_index, 0, qubit_index
                    )
                    candidate_state = candidate_state.apply_ry(qubit_index, -cry_theta)

                    thetas = candidate_state.get_ry_angles(qubit_index)
                    most_frequent_theta = Counter(thetas).most_common(1)[0][0]
                    candidate_state = candidate_state.apply_ry(
                        qubit_index, -most_frequent_theta
                    )

                    thetas = candidate_state.get_ry_angles(qubit_index)

                    final_score = len(thetas) - thetas.count(0)

                    curr_score = initial_score - final_score

                    print(f"state after: {candidate_state} score {final_score}")
                    if curr_score > best_score:
                        best_score = curr_score
                        best_qubit_index = qubit_index
                        best_control_qubit_index = control_qubit_index
                        best_cry_theta = cry_theta
                        best_ry_theta = most_frequent_theta

        if best_qubit_index is not None:
            print(
                f"best qubit: {best_qubit_index}, best control qubit: {best_control_qubit_index}, best cry theta: {best_cry_theta}"
            )

            assert best_qubit_index is not None
            assert best_cry_theta is not None
            assert best_ry_theta is not None
            best_ry_theta: float
            best_cry_theta: float

            curr_state = curr_state.apply_ry(best_qubit_index, best_cry_theta)
            curr_state = curr_state.apply_cx(
                best_control_qubit_index, 0, best_qubit_index
            )
            curr_state = curr_state.apply_ry(best_qubit_index, -best_cry_theta)
            curr_state = curr_state.apply_ry(best_qubit_index, -best_ry_theta)

            # we add the gates
            gates.append(qc.RY(-best_cry_theta, circuit.qubit_at(best_qubit_index)))
            gates.append(
                qc.CX(
                    circuit.qubit_at(best_control_qubit_index),
                    0,
                    circuit.qubit_at(best_qubit_index),
                )
            )
            gates.append(qc.RY(best_cry_theta, circuit.qubit_at(best_qubit_index)))
            gates.append(qc.RY(best_ry_theta, circuit.qubit_at(best_qubit_index)))

    return gates[::-1]
