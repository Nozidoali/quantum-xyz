#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-21 22:42:21
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-22 01:42:29
"""
import copy
import numpy as np
from typing import Tuple
from collections import Counter

from xyz.qstate import QState
import xyz.circuit as qc

from .library import Library


def rotation(curr_state_pair: Tuple, circuit: qc.QCircuit):
    """AI is creating summary for rotation

    :param curr_state: [description]
    :type curr_state: QState
    :param next_state: [description]
    :type next_state: QState
    :param qubit: [description]
    :type qubit: int
    :param theta: [description]
    :type theta: float
    """

    curr_cost, curr_state = curr_state_pair
    supports = curr_state.get_supports()

    for qubit_index in supports:
        thetas = curr_state.get_ry_angles(qubit_index)
        most_frequent_theta, frequency = Counter(thetas).most_common(1)[0]
        if not np.isclose(
            most_frequent_theta, 0, atol=1e-2
        ) and frequency > thetas.count(0):
            # then we apply and return
            next_state = curr_state.apply_ry(qubit_index, -most_frequent_theta)

            gates = []
            gates.append(qc.RY(most_frequent_theta, circuit.qubit_at(qubit_index)))
            return (curr_cost, next_state), gates[:]

    return None, []


def reflection(curr_state_pair: Tuple, circuit: qc.QCircuit):
    """Perform reflection of the current circuit .

    :param curr_state_pair: [description]
    :type curr_state_pair: Tuple
    :param circuit: [description]
    :type circuit: qc.QCircuit
    :return: [description]
    :rtype: [type]
    """

    curr_cost: int
    curr_state: QState

    curr_cost, curr_state = curr_state_pair
    supports = curr_state.get_supports()

    for qubit_index in supports:
        thetas = curr_state.get_ry_angles(qubit_index)
        initial_score = len(thetas) - thetas.count(0)

        rotation_table = curr_state.get_rotation_table(qubit_index)
        rotation_table_str = "\n".join(
            [
                f"{bin(idx)[2:].zfill(curr_state.num_qubits)}: {theta}"
                for idx, theta in rotation_table.items()
            ]
        )
        print(f"rotation table: \n{rotation_table_str}\n\n")

        for control_qubit_index in supports:
            if control_qubit_index == qubit_index:
                continue

            cry_thetas = curr_state.get_cry_angles(control_qubit_index, qubit_index)

            for cry_theta in cry_thetas:
                candidate_state: QState = copy.deepcopy(curr_state)
                candidate_state = candidate_state.apply_ry(qubit_index, cry_theta)
                candidate_state = candidate_state.apply_cx(
                    control_qubit_index, 0, qubit_index
                )
                candidate_state = candidate_state.apply_ry(qubit_index, -cry_theta)

                thetas = candidate_state.get_ry_angles(qubit_index)

                # if not np.isclose(
                #     most_frequent_theta, 0, atol=1e-2
                # ) and frequency > thetas.count(0):
                #     candidate_state = candidate_state.apply_ry(
                #         qubit_index, -most_frequent_theta
                #     )

                thetas = candidate_state.get_ry_angles(qubit_index)
                final_score = len(thetas) - thetas.count(0)
                curr_score = initial_score - final_score

                # this is tricky
                # if we only accept the state with lower cost, then we will not be able to reach the ground state
                # if curr_score < 0:
                if curr_score == 0:
                    continue

                # we add the gates
                gates = []
                # gates.append(qc.RY(most_frequent_theta, circuit.qubit_at(qubit_index)))
                gates.append(qc.RY(cry_theta, circuit.qubit_at(qubit_index)))
                gates.append(
                    qc.CX(
                        circuit.qubit_at(control_qubit_index),
                        0,
                        circuit.qubit_at(qubit_index),
                    )
                )
                gates.append(qc.RY(-cry_theta, circuit.qubit_at(qubit_index)))

                yield (curr_cost + 1, candidate_state), gates[:]

    return None, []


def cx(curr_state_pair: Tuple, circuit: qc.QCircuit):
    """Perform CX of the current circuit .

    :param curr_state_pair: [description]
    :type curr_state_pair: Tuple
    :param circuit: [description]
    :type circuit: qc.QCircuit
    :return: [description]
    :rtype: [type]
    """

    curr_cost, curr_state = curr_state_pair
    supports = curr_state.get_supports()

    for control_qubit_index in supports:
        for target_qubit_index in supports:
            if control_qubit_index == target_qubit_index:
                continue

            candidate_state: QState = copy.deepcopy(curr_state)
            candidate_state = candidate_state.apply_cx(
                control_qubit_index, 0, target_qubit_index
            )

            gates = []
            gates.append(
                qc.CX(
                    circuit.qubit_at(control_qubit_index),
                    0,
                    circuit.qubit_at(target_qubit_index),
                )
            )

            yield (curr_cost + 1, candidate_state), gates[:]

    return None, []


class DefaultLibrary(Library):
    """A default library class .

    :param Library: [description]
    :type Library: [type]
    """

    def explore(self):
        n_visited: int = 0

        while not self.state_queue.empty():
            curr_state_pair = self.state_queue.get()

            curr_cost: int
            curr_state: QState
            curr_cost, curr_state = curr_state_pair

            curr_repr = curr_state.repr()
            self.visited_states.add(curr_repr)
            self.record[curr_state] = curr_cost

            n_visited += 1
            if n_visited % 100 == 0:
                print(
                    f"#enquened states: {len(self.enquened_states)}, #visited states: {len(self.visited_states)}, current cost: {curr_cost}"
                )

            if curr_state == QState.ground_state(self.num_qubits):
                break

            next_state_pair, gates = rotation(curr_state_pair, self.circuit)
            if next_state_pair is not None:
                self.explore_state(curr_state_pair, next_state_pair, gates)
                continue

            for next_state_pair, gates in reflection(curr_state_pair, self.circuit):
                if next_state_pair is not None:
                    self.explore_state(curr_state_pair, next_state_pair, gates)
                    continue

            # for next_state_pair, gates in cx(curr_state_pair, self.circuit):
            #     if next_state_pair is not None:
            #         self.explore_state(curr_state_pair, next_state_pair, gates)
            #         continue

        return
