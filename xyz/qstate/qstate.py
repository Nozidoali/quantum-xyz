#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-12 03:02:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:40:18
"""

import json

from typing import List, Tuple
import numpy as np

# the merge uncertainty, if the difference between the two angles is less than
# this value, we consider them to be the same
MERGE_UNCERTAINTY = 1e-3


N_DIGITS = 2


class QState:
    """Class method for QState"""

    from ._rotation_angles import (
        get_cry_angles,
        get_ry_angles,
        get_most_frequent_theta,
        get_rotation_table,
    )

    def __init__(self, index_to_weight: dict, num_qubit: int) -> None:
        self.num_qubits = num_qubit

        self.index_to_weight = {}
        for index, weight in index_to_weight.items():
            if not np.isclose(weight, 0, atol=1e-3):
                self.index_to_weight[index] = weight
        self.index_set = self.index_to_weight.keys()

        self.sparsity: int = len(index_to_weight)

    def __deepcopy__(self, memo):
        return QState(self.index_to_weight, self.num_qubits)

    def apply_x(self, qubit_index: int) -> "QState":
        """Apply X gate to the qubit.

        :param qubit_index: [description]
        :type qubit_index: int
        """
        index_to_weight = {}
        for idx in self.index_set:
            reversed_idx = idx ^ (1 << qubit_index)
            index_to_weight[reversed_idx] = self.index_to_weight[idx]
        return QState(index_to_weight, self.num_qubits)

    def apply_cx(
        self, control_qubit_index: int, phase: bool, target_qubit_index: int
    ) -> "QState":
        """Apply CX gate to the qubit.

        :param control_qubit_index: [description]
        :type control_qubit_index: int
        :param target_qubit_index: [description]
        :type target_qubit_index: int
        """
        index_to_weight = {}
        for idx, weight in self.index_to_weight.items():
            reversed_idx = idx ^ (1 << target_qubit_index)
            if (idx >> control_qubit_index) & 1 == phase:
                index_to_weight[reversed_idx] = weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, self.num_qubits)

    def apply_ry(self, qubit_index: int, theta: float) -> "QState":
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        index_to_weight = {idx: 0 for idx in self.index_set}
        for idx, weight in self.index_to_weight.items():
            rdx = idx ^ (1 << qubit_index)
            if rdx not in self.index_set:
                index_to_weight[rdx] = 0

            if idx >> qubit_index & 1 == 0:
                index_to_weight[idx] += weight * np.cos(theta / 2)
                index_to_weight[rdx] += weight * np.sin(theta / 2)
            else:
                index_to_weight[idx] += weight * np.cos(theta / 2)
                index_to_weight[rdx] -= weight * np.sin(theta / 2)
        return QState(index_to_weight, self.num_qubits)

    def apply_merge0(self, qubit_index: int) -> "QState":
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        index_to_weight = {}
        theta = None
        for idx in self.index_set:
            reversed_idx = idx ^ (1 << qubit_index)
            if reversed_idx not in self.index_set:
                raise ValueError("The state is not a valid state.")
            idx0 = idx & ~(1 << qubit_index)
            idx1 = idx0 ^ (1 << qubit_index)

            # now we check the rotation angle
            weight_from = self.index_to_weight[idx0]
            weight_to = self.index_to_weight[idx1]
            weight_total = np.sqrt(
                (self.index_to_weight[idx1] ** 2) + (self.index_to_weight[idx0] ** 2)
            )

            _theta = 2 * np.arctan(weight_to / weight_from)

            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta, atol=MERGE_UNCERTAINTY):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx0] = weight_total
        if theta is None:
            raise ValueError("The state is not a valid state.")
        return QState(index_to_weight, self.num_qubits), theta

    def apply_merge1(self, qubit_index: int) -> "QState":
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        index_to_weight = {}
        theta = None
        for idx in self.index_set:
            reversed_idx = idx ^ (1 << qubit_index)
            if reversed_idx not in self.index_set:
                raise ValueError("The state is not a valid state.")
            idx0 = idx & ~(1 << qubit_index)
            idx1 = idx0 ^ (1 << qubit_index)

            # now we check the rotation angle
            weight0 = self.index_to_weight[idx0]
            weight1 = self.index_to_weight[idx1]
            weight_total = np.sqrt(
                (weight0 ** 2) + (weight1 ** 2)
            )

            _theta = 2 * np.arctan(weight0 / weight1)

            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta, atol=MERGE_UNCERTAINTY):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx1] = weight_total
        if theta is None:
            raise ValueError("The state is not a valid state.")
        return QState(index_to_weight, self.num_qubits), theta

    def apply_split(self, qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        new_states = []
        for state in self.index_set:
            state0 = state & ~(1 << qubit_index)
            state1 = state | (1 << qubit_index)

            new_states.append(state0)
            new_states.append(state1)

        next_state = QState(new_states, self.num_qubits)
        return next_state

    def apply_controlled_merge0(
        self, control_qubit_index: int, phase: bool, target_qubit_index: int
    ) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        index_to_weight = {}
        theta = None
        for idx in self.index_set:
            # no rotation
            if (idx >> control_qubit_index) & 1 != phase:
                index_to_weight[idx] = self.index_to_weight[idx]
                continue

            reversed_idx = idx ^ (1 << target_qubit_index)
            if reversed_idx not in self.index_set:
                raise ValueError("The state is not a valid state.")
            idx0 = idx & ~(1 << target_qubit_index)
            idx1 = idx0 ^ (1 << target_qubit_index)

            # now we check the rotation angle
            weight_from = self.index_to_weight[idx0]
            weight_to = self.index_to_weight[idx1]
            weight_total = np.sqrt(
                (self.index_to_weight[idx1] ** 2) + (self.index_to_weight[idx0] ** 2)
            )

            _theta = 2 * np.arctan(weight_to / weight_from)

            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta, atol=MERGE_UNCERTAINTY):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx0] = weight_total
        if theta is None:
            raise ValueError("The state is not a valid state.")
        return QState(index_to_weight, self.num_qubits), theta

    def apply_controlled_merge1(
        self, control_qubit_index: int, phase: bool, target_qubit_index: int
    ) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        index_to_weight = {}
        theta = None
        for idx in self.index_set:
            # no rotation
            if (idx >> control_qubit_index) & 1 != phase:
                index_to_weight[idx] = self.index_to_weight[idx]
                continue

            reversed_idx = idx ^ (1 << target_qubit_index)
            if reversed_idx not in self.index_set:
                raise ValueError("The state is not a valid state.")
            idx0 = idx & ~(1 << target_qubit_index)
            idx1 = idx0 ^ (1 << target_qubit_index)

            # now we check the rotation angle
            weight0 = self.index_to_weight[idx0]
            weight1 = self.index_to_weight[idx1]
            weight_total = np.sqrt(
                (weight0 ** 2) + (weight1 ** 2)
            )

            _theta = 2 * np.arctan(weight0 / weight1)

            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta, atol=MERGE_UNCERTAINTY):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx1] = weight_total
        if theta is None:
            raise ValueError("The state is not a valid state.")
        return QState(index_to_weight, self.num_qubits), theta

    def get_supports(self) -> List[int]:
        """Return the support of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: List[int]
        """
        signatures = self.get_qubit_signatures()
        qubit_indices = []
        for qubit, pattern in enumerate(signatures):
            if pattern != 0:
                qubit_indices.append(qubit)
        return qubit_indices

    def get_sparsity(self) -> int:
        """Return the sparsity of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """
        return len(self.index_set)

    def to_value(self) -> int:
        """Return the value of the state .

        :return: [description]
        :rtype: int
        """
        value = 0
        for basis in self.index_set:
            value |= 1 << basis
        return value

    def get_qubit_signatures(self) -> List[int]:
        """Transpose the state array ."""
        signatures = [0 for i in range(self.num_qubits)]
        for _, value in enumerate(self.index_set):
            for j in range(self.num_qubits):
                signatures[j] = signatures[j] << 1 | (value >> j & 1)
        return signatures

    def get_const1_signature(self) -> int:
        """Returns the number of signed unsigned signatures .

        :return: [description]
        :rtype: int
        """
        return (1 << len(self.index_set)) - 1

    def cofactors(self, pivot_qubit: int) -> Tuple["QState", "QState"]:
        """Returns the cofactors of the given qubit .

        :return: [description]
        :rtype: [type]
        """

        index_to_weight0 = {}
        index_to_weight1 = {}

        total_weights0 = 0
        total_weights1 = 0

        for idx in self.index_set:
            if (idx >> pivot_qubit) & 1 == 0:
                index_to_weight0[idx] = self.index_to_weight[idx]
                total_weights0 += self.index_to_weight[idx]
            else:
                index_to_weight1[idx ^ (1 << pivot_qubit)] = self.index_to_weight[idx]
                total_weights1 += self.index_to_weight[idx]

        return (
            QState(index_to_weight0, self.num_qubits),
            QState(index_to_weight1, self.num_qubits),
            total_weights0,
            total_weights1,
        )

    @staticmethod
    def ground_state(num_qubits: int) -> "QState":
        """Return the ground state .

        :param num_qubits: [description]
        :type num_qubits: int
        :return: [description]
        :rtype: QState
        """
        state = QState({0: 1.0}, num_qubits)
        return state

    def get_lower_bound(self) -> int:
        """Returns the lower bound of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """
        lower_bound: int = 0
        signatures = self.get_qubit_signatures()
        for pattern in signatures:
            if pattern != 0:
                lower_bound += 1
        return lower_bound

    def __str__(self) -> str:
        return " + ".join(
            [
                f"{weight.real:0.0{N_DIGITS}f}*|{idx:0{self.num_qubits}b}>".zfill(
                    self.num_qubits
                )
                for idx, weight in self.index_to_weight.items()
            ]
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QState):
            return False
        return self.__hash__() == other.__hash__()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, QState):
            return False
        sorted_index_set = sorted(self.index_set, reverse=True)
        sorted_o_index_set = sorted(other.index_set, reverse=True)
        for i, index in enumerate(sorted_index_set):
            if i >= len(sorted_o_index_set):
                return False
            if index < sorted_o_index_set[i]:
                return True
            elif index > sorted_o_index_set[i]:
                return False
        return False

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.index_set)))
        # return hash(str(self))

    def repr(self) -> int:
        """Return a hex representation of the bitmap .

        :return: [description]
        :rtype: int
        """
        # self.index_set = sorted(self.index_set)
        # signatures = self.get_qubit_signatures()
        # return hash(tuple(sorted(signatures, key=lambda x: bin(x).count("1"))))
        return hash(self)

    def to_vector(self) -> np.ndarray:
        """Return the vector representation of the state .

        :return: [description]
        :rtype: np.ndarray
        """
        vector = np.zeros(2**self.num_qubits)
        for idx, weight in self.index_to_weight.items():
            vector[idx] = np.sqrt(weight)

        # normalize the vector
        vector /= np.linalg.norm(vector)

        return vector

    def to_file(self, filename: str):
        """Writes the benchmark to a file .

        :param filename: [description]
        :type filename: str
        """

        # we format the index as a string
        index_to_weight = {
            f"{index:0{self.num_qubits}b}": weight
            for index, weight in self.index_to_weight.items()
        }
        benchmark_str = json.dumps(index_to_weight)
        # lets be safe here

        with open(filename, "w", encoding="utf-8") as file:
            file.write(benchmark_str)


def quantize_state(state_vector: np.ndarray):
    """Quantize a state to the number of qubits .

    :param state_vector: a vector with 2**n entries, where n is the number of qubits.
    :type state_vector: np.ndarray
    """

    # discard the imaginary part
    # state_vector = state_vector.real
    state_vector = np.real(state_vector)

    # normalize the vector
    state_vector = state_vector.astype(np.float64) / np.linalg.norm(
        state_vector.astype(np.float64)
    )

    index_to_weight = {}
    num_qubits = int(np.log2(len(state_vector)))
    for idx, coefficient in enumerate(state_vector):
        if not np.isclose(coefficient, 0):
            index_to_weight[idx] = coefficient
    return QState(index_to_weight, num_qubits)


def load_state(filename: str):
    """Loads the state of a given file .

    :param filename: [description]
    :type filename: str
    """

    # read the dict from the file
    with open(filename, "r", encoding="utf-8") as file:
        state_dict = json.load(file)

    num_qubits: int = None
    index_to_weight = {}
    for index_str, weight in state_dict.items():
        if num_qubits is None:
            num_qubits = len(index_str)

        index = int(index_str, 2)
        index_to_weight[index] = weight

    # convert the dict to a QState
    return QState(index_to_weight, num_qubits)


def from_val(val: int, num_qubits: int) -> QState:
    """Return the state from the vector representation .

    :param state_vector: [description]
    :type state_vector: np.ndarray
    :return: [description]
    :rtype: QState
    """

    assert val > 0 and val < 2 ** (2**num_qubits)
    states = []
    for i in range(2**num_qubits):
        if val & 1 == 1:
            states.append(i)
        val >>= 1

    patterns = [0 for i in range(num_qubits)]
    for _, value in enumerate(states):
        for j in range(num_qubits):
            patterns[j] = patterns[j] << 1 | ((value >> j) & 1)
    return QState(patterns, len(states))
