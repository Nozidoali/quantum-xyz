#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-12 03:02:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:40:18
"""

from typing import List
import numpy as np
import copy


class QState:
    """Class method for QState"""

    def __init__(self, index_to_weight: dict, num_qubit: int) -> None:
        self.num_qubits = num_qubit
        self.sparsity: int = len(index_to_weight)
        self.index_set = index_to_weight.keys()
        self.index_to_weight = copy.deepcopy(index_to_weight)

    def get_supports(self) -> List[int]:
        """Return the support of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: List[int]
        """
        signatures = self.to_signatures()
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

    def apply_x(self, qubit_index: int) -> None:
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
    ) -> None:
        """Apply CX gate to the qubit.

        :param control_qubit_index: [description]
        :type control_qubit_index: int
        :param target_qubit_index: [description]
        :type target_qubit_index: int
        """
        index_to_weight = {}
        for idx in self.index_set:
            reversed_idx = idx ^ (1 << target_qubit_index)
            if (idx >> control_qubit_index) & 1 == phase:
                index_to_weight[reversed_idx] = self.index_to_weight[idx]
            else:
                index_to_weight[idx] = self.index_to_weight[idx]
        return QState(index_to_weight, self.num_qubits)

    def apply_merge0(self, qubit_index: int) -> None:
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
            _theta = 2 * np.arccos(
                np.sqrt(
                    self.index_to_weight[idx0]
                    / (self.index_to_weight[idx0] + self.index_to_weight[idx1])
                )
            )
            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx0] = (
                self.index_to_weight[idx0] + self.index_to_weight[idx1]
            )
        if theta is None:
            raise ValueError("The state is not a valid state.")
        return QState(index_to_weight, self.num_qubits), theta

    def apply_merge1(self, qubit_index: int) -> None:
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
            _theta = 2 * np.arccos(
                np.sqrt(
                    self.index_to_weight[idx1]
                    / (self.index_to_weight[idx0] + self.index_to_weight[idx1])
                )
            )
            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx1] = (
                self.index_to_weight[idx0] + self.index_to_weight[idx1]
            )
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
            _theta = 2 * np.arccos(
                np.sqrt(
                    self.index_to_weight[idx0]
                    / (self.index_to_weight[idx0] + self.index_to_weight[idx1])
                )
            )
            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx0] = (
                self.index_to_weight[idx0] + self.index_to_weight[idx1]
            )
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
            _theta = 2 * np.arccos(
                np.sqrt(
                    self.index_to_weight[idx1]
                    / (self.index_to_weight[idx0] + self.index_to_weight[idx1])
                )
            )
            if theta is None:
                theta = _theta
            elif not np.isclose(theta, _theta):
                raise ValueError("The state is not a valid state.")

            # finally we update the weight
            index_to_weight[idx1] = (
                self.index_to_weight[idx0] + self.index_to_weight[idx1]
            )
        if theta is None:
            raise ValueError("The state is not a valid state.")
        return QState(index_to_weight, self.num_qubits), theta

    def to_signatures(self) -> List[int]:
        """Transpose the state array ."""
        signatures = [0 for i in range(self.num_qubits)]
        for _, value in enumerate(self.index_set):
            for j in range(self.num_qubits):
                signatures[j] = signatures[j] << 1 | (value >> j & 1)
        return signatures

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
        signatures = self.to_signatures()
        for pattern in signatures:
            if pattern != 0:
                lower_bound += 1
        return lower_bound

    def __str__(self) -> str:
        return " + ".join(
            [
                f"{np.sqrt(weight):0.02f}*|{idx:0{self.num_qubits}b}>".zfill(
                    self.num_qubits
                )
                for idx, weight in self.index_to_weight.items()
            ]
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return self.__hash__() == o.__hash__()

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return False

    def __hash__(self) -> int:
        value = 0
        for index in sorted(self.index_set):
            value = value << self.num_qubits | index
        return value


def quantize_state(state_vector: np.ndarray):
    """Quantize a state to the number of qubits .

    :param state_vector: [description]
    :type state_vector: np.ndarray
    """

    index_to_weight = {}
    num_qubits = int(np.log2(len(state_vector)))
    for idx, coefficient in enumerate(state_vector):
        if coefficient != 0:
            index_to_weight[idx] = coefficient**2
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
