#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-12 03:02:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:40:18
"""

from typing import List
from itertools import permutations

import copy
import numpy as np


class QState:
    """Class method for QState"""

    def __init__(self, state_array: np.ndarray, num_qubits: int) -> None:
        self.patterns = [0 for i in range(num_qubits)]
        self.num_qubits = num_qubits
        self.length: int = 0
        self.const_one: int = 1 << num_qubits - 1
        for i in range(2**num_qubits):
            if state_array[i] != 0:
                for j in range(num_qubits):
                    self.patterns[j] = self.patterns[j] << 1 | (i >> j & 1)
                self.length += 1

    def __len__(self) -> int:
        num_ones: int = 0
        for j in range(self.num_qubits):
            num_ones += self.patterns[j]
        return num_ones

    def num_supports(self) -> int:
        """Returns the number of supported supports supports .

        :return: [description]
        :rtype: int
        """
        return 0

    def count_ones(self) -> int:
        """Returns the number of ones in the state array.


        :return: [description]
        :rtype: int
        """
        one_counts = {qubit_index: 0 for qubit_index in range(self.num_qubits)}
        for qubit_index in range(self.num_qubits):
            pattern = self.patterns[qubit_index]
            for _ in range(self.length):
                if pattern & 1 == 1:
                    one_counts[qubit_index] += 1
                pattern >>= 1

        return one_counts

    def apply_x(self, qubit_index: int) -> None:
        """Apply X gate to the qubit.

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        next_state.patterns[qubit_index] = self.const_one ^ self.patterns[qubit_index]
        return next_state

    def apply_cx(self, control_qubit_index: int, target_qubit_index: int) -> None:
        """Apply CX gate to the qubit.

        :param control_qubit_index: [description]
        :type control_qubit_index: int
        :param target_qubit_index: [description]
        :type target_qubit_index: int
        """
        next_state = copy.deepcopy(self)
        next_state.patterns[target_qubit_index] ^= self.patterns[control_qubit_index]
        return next_state

    def apply_merge0(self, qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        self.patterns[qubit_index] = 0

    def __transpose(self) -> List[int]:
        """Transpose the state array ."""
        values = [0 for i in range(self.length)]
        for qubit_index in range(self.num_qubits):
            pattern = self.patterns[qubit_index]
            for i in range(self.length):
                values[i] = values[i] << 1 | (pattern & 1)
                pattern >>= 1
        return values

    def cleanup_columns(self) -> None:
        """Remove the redundant supports supports ."""
        values = self.__transpose()
        values = set(values)
        self.length = len(values)
        self.patterns = [0 for i in range(self.num_qubits)]
        for _, value in enumerate(values):
            for j in range(self.num_qubits):
                self.patterns[j] = self.patterns[j] << 1 | (value >> j & 1)

    def all_column_permutations(self):
        """Generator over all permutations of all columns in the DataFrame .

        :yield: [description]
        :rtype: [type]
        """
        values = self.__transpose()
        for perm in permutations(values):
            # transpose back
            patterns = [0 for i in range(self.num_qubits)]
            for _, value in enumerate(perm):
                for j in range(self.num_qubits):
                    patterns[j] = patterns[j] << 1 | (value >> j & 1)

            yield patterns

    def representative(self) -> "QState":
        """Return a repr string for this object ."""
        repr_state = copy.deepcopy(self)

        # remove redundant columns, update length
        repr_state.cleanup_columns()

        for patterns in repr_state.all_column_permutations():
            # run x and qubit permutations
            for qubit_index in range(repr_state.num_qubits):
                # apply X gate to reduce pattern
                if patterns[qubit_index] >> (self.length - 1) == 1:
                    patterns[qubit_index] = repr_state.const_one ^ patterns[qubit_index]

            # sort patterns
            patterns = sorted(patterns)

            # check if this is the smallest
            is_smallest = True
            for i in range(repr_state.num_qubits):
                if patterns[i] > repr_state.patterns[i]:
                    is_smallest = False
                    break

            # update if this is the smallest
            if is_smallest:
                repr_state.patterns = copy.deepcopy(patterns)

        return repr_state

    def is_ground_state(self) -> None:
        """True if the current state is a ground state .

        :return: [description]
        :rtype: [type]
        """
        return len(self) == 0

    def __str__(self) -> str:
        return "-".join([f"{x:b}".zfill(self.length) for x in self.patterns])

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return self.patterns == o.patterns

    def __lt__(self, o: object) -> bool:
        if not isinstance(o, QState):
            return False
        return len(self) < len(o)

    def __hash__(self) -> int:
        ret_val: int = 1
        for pattern in self.patterns:
            ret_val <<= self.length
            ret_val |= int(pattern)
        return hash(ret_val)
