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

    def __init__(self, patterns: List[int], sparsity: int) -> None:
        self.const_one: int = (1 << sparsity) - 1
        self.signature_length: int = sparsity
        
        # patterns
        self.num_qubits = len(patterns)
        self.patterns = patterns[:]
        
        # sparsity
        self.sparsity: int = sparsity
        self.index_set = self.to_index_set()
        
        # weights (lets imagine that the weights are all 1)
        self.index_to_weight = {index: 1 for index in self.index_set}

    def to_value(self) -> int:
        """Return the value of the state .

        :return: [description]
        :rtype: int
        """
        states = self.to_index_set()[:]
        value = 0
        for basis in states:
            value |= 1 << basis
        return value

    def __len__(self) -> int:
        num_ones: int = 0
        for j in range(self.num_qubits):
            num_ones += self.patterns[j]
        return num_ones

    def apply_x(self, qubit_index: int) -> None:
        """Apply X gate to the qubit.

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        next_state.patterns[qubit_index] = self.const_one ^ self.patterns[qubit_index]
        return next_state

    def apply_cx(
        self, control_qubit_index: int, phase: bool, target_qubit_index: int
    ) -> None:
        """Apply CX gate to the qubit.

        :param control_qubit_index: [description]
        :type control_qubit_index: int
        :param target_qubit_index: [description]
        :type target_qubit_index: int
        """
        next_state = copy.deepcopy(self)
        next_state.patterns[target_qubit_index] ^= self.patterns[control_qubit_index]
        if not phase:
            next_state.patterns[target_qubit_index] = (
                ~next_state.patterns[target_qubit_index] & self.const_one
            )
        return next_state

    def apply_merge0(self, qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        next_state.patterns[qubit_index] = 0
        next_state.cleanup_columns()
        return next_state

    def apply_split(self, qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        states = self.to_index_set()
        new_states = []
        for state in states:
            state0 = state & ~(1 << qubit_index)
            state1 = state | (1 << qubit_index)

            new_states.append(state0)
            new_states.append(state1)

        patterns = self.transpose_back(new_states)
        next_state = QState(patterns, len(new_states))
        return next_state

    def apply_controlled_merge0(
        self, control_qubit_index: int, phase: bool, target_qubit_index: int
    ) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        control = (
            ~self.patterns[control_qubit_index]
            if phase
            else self.patterns[control_qubit_index]
        )
        next_state.patterns[target_qubit_index] &= control
        next_state.cleanup_columns()
        return next_state

    def apply_controlled_merge1(
        self, control_qubit_index: int, phase: bool, target_qubit_index: int
    ) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        control = (
            ~self.patterns[control_qubit_index]
            if phase
            else self.patterns[control_qubit_index]
        )
        next_state.patterns[target_qubit_index] |= control
        next_state.cleanup_columns()
        return next_state

    def to_index_set(self) -> List[int]:
        """Transpose the state array ."""
        basis = [0 for i in range(self.sparsity)]
        for i in range(self.sparsity):
            for qubit_index in range(self.num_qubits):
                pattern = self.patterns[qubit_index] & self.const_one
                digit = ((pattern >> i) & 1) << qubit_index
                basis[i] |= digit
        return basis

    def cofactors(self, qubit_index: int) -> List[int]:
        """Return the cofactor of the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        pos_cofactor = set()
        neg_cofactor = set()
        for i in range(self.sparsity):
            value = 0
            for j in range(self.num_qubits):
                value <<= 1
                if j == qubit_index:
                    continue
                value |= (self.patterns[j] >> i) & 1

            if (self.patterns[qubit_index] >> i) & 1 == 1:
                pos_cofactor.add(value)
            else:
                neg_cofactor.add(value)

        return pos_cofactor, neg_cofactor

    def controlled_cofactors(
        self, qubit_index: int, control_qubit: int, phase: bool
    ) -> List[int]:
        """Return the cofactor of the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        pos_cofactor = set()
        neg_cofactor = set()
        for i in range(self.sparsity):
            if (self.patterns[control_qubit] >> i) & 1 != phase:
                continue

            value = 0
            for j in range(self.num_qubits):
                value <<= 1
                if j == qubit_index:
                    continue
                value |= (self.patterns[j] >> i) & 1

            if (self.patterns[qubit_index] >> i) & 1 == 1:
                pos_cofactor.add(value)
            else:
                neg_cofactor.add(value)

        return pos_cofactor, neg_cofactor

    def cleanup_columns(self) -> None:
        """Remove the redundant supports supports ."""
        values = self.to_index_set()

        # remove redundant columns
        values = set(values)
        self.sparsity = len(values)
        self.const_one = (1 << self.sparsity) - 1
        self.patterns = [0 for i in range(self.num_qubits)]

        # now we sort the values
        values = sorted(values)

        self.patterns = self.transpose_back(values)

    def get_x_signatures(self) -> List[int]:
        """Returns the indices of the X - signature of the QR code .

        :return: [description]
        :rtype: List[int]
        """

        signatures = []
        for qubit_index in range(self.num_qubits):
            if self.patterns[qubit_index] & 1 == 1:
                signatures.append(qubit_index)

        return signatures

    def get_y_signatures(self) -> List[int]:
        """Returns the indices of the Y - signature of the QR code .

        :return: [description]
        :rtype: List[int]
        """

        signatures = []
        for qubit_index in range(self.num_qubits):
            pos_cofactor, neg_cofactor = self.cofactors(qubit_index)

            if len(pos_cofactor) != 0 and pos_cofactor == neg_cofactor:
                signatures.append(qubit_index)

        return signatures

    def transpose_back(self, values: List[int]) -> List[int]:
        """Transpose the state array ."""
        patterns = [0 for i in range(self.num_qubits)]
        for _, value in enumerate(values):
            for j in range(self.num_qubits):
                patterns[j] = patterns[j] << 1 | (value >> j & 1)
        return patterns

    def is_ground_state(self) -> None:
        """True if the current state is a ground state .

        :return: [description]
        :rtype: [type]
        """
        return self.sparsity == 1

    @staticmethod
    def ground_state(num_qubits: int) -> "QState":
        """Return the ground state .

        :param num_qubits: [description]
        :type num_qubits: int
        :return: [description]
        :rtype: QState
        """
        state = QState([0 for i in range(num_qubits)], 1)
        return state

    def get_lower_bound(self) -> int:
        """Returns the lower bound of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """

        lower_bound: int = 0
        for pattern in self.patterns:
            if pattern != 0:
                lower_bound += 1
        return lower_bound

    def __str__(self) -> str:
        return "+".join([f"{x:b}".zfill(self.sparsity) for x in self.patterns])

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return self.__hash__() == o.__hash__()

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return len(self) < len(o)

    def __hash__(self) -> int:
        ret_val: int = 0
        for pattern in self.patterns:
            ret_val = (ret_val << self.signature_length) | (pattern & self.const_one)
        return hash(ret_val)


def quantize_state(state_vector: np.ndarray):
    """Quantize a state to the number of qubits .

    :param state_vector: [description]
    :type state_vector: np.ndarray
    """

    states = []
    num_qubits = int(np.log2(len(state_vector)))
    for state, coefficient in enumerate(state_vector):
        if coefficient != 0:
            states.append(state)

    patterns = [0 for i in range(num_qubits)]
    for _, value in enumerate(states):
        for j in range(num_qubits):
            patterns[j] = patterns[j] << 1 | ((value >> j) & 1)
    return QState(patterns, len(states))


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
