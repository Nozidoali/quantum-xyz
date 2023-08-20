#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-12 03:02:33
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-19 13:40:18
"""

from typing import List

import copy
import numpy as np

class QState:
    """Class method for QState"""

    def __init__(self, state_array: np.ndarray, num_qubits: int) -> None:
        self.patterns = [0 for i in range(num_qubits)]
        self.num_qubits = num_qubits
        self.length: int = 0
        self.const_one: int = (1 << num_qubits) - 1
        for i in range(2**num_qubits):
            if state_array[i] != 0:
                for j in range(num_qubits):
                    self.patterns[j] = self.patterns[j] << 1 | (i >> j & 1)
                self.length += 1
        self.signature_length: int = self.length
    
    # canonicalization
    from .representative import representative

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

    def apply_cx(self, control_qubit_index: int, phase: bool, target_qubit_index: int) -> None:
        """Apply CX gate to the qubit.

        :param control_qubit_index: [description]
        :type control_qubit_index: int
        :param target_qubit_index: [description]
        :type target_qubit_index: int
        """
        next_state = copy.deepcopy(self)
        next_state.patterns[target_qubit_index] ^= self.patterns[control_qubit_index]
        if phase:
            next_state.patterns[target_qubit_index] = ~next_state.patterns[target_qubit_index] & self.const_one
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
    
    def apply_controlled_merge0(self, control_qubit_index: int, phase: bool, target_qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        control = ~self.patterns[control_qubit_index] if phase else self.patterns[control_qubit_index]
        next_state.patterns[target_qubit_index] &= control
        next_state.cleanup_columns()
        return next_state

    def apply_controlled_merge1(self, control_qubit_index: int, phase: bool, target_qubit_index: int) -> None:
        """Apply the Y operator to the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        next_state = copy.deepcopy(self)
        control = ~self.patterns[control_qubit_index] if phase else self.patterns[control_qubit_index]
        next_state.patterns[target_qubit_index] |= control
        next_state.cleanup_columns()
        return next_state

    def transpose(self) -> List[int]:
        """Transpose the state array ."""
        values = [0 for i in range(self.length)]
        for qubit_index in range(self.num_qubits):
            pattern = self.patterns[qubit_index]
            for i in range(self.length):
                values[i] = values[i] << 1 | (pattern & 1)
                pattern >>= 1
        return values
    
    def cofactors(self, qubit_index: int) -> List[int]:
        """Return the cofactor of the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        pos_cofactor = set()
        neg_cofactor = set()
        for i in range(self.length):
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

    def controlled_cofactors(self, qubit_index: int, control_qubit: int, phase: bool) -> List[int]:
        """Return the cofactor of the given qubit .

        :param qubit_index: [description]
        :type qubit_index: int
        """
        pos_cofactor = set()
        neg_cofactor = set()
        for i in range(self.length):
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
        values = self.transpose()
        
        # remove redundant columns
        values = set(values)
        self.length = len(values)
        self.const_one = (1 << self.length) - 1
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
        return self.length == 1

    
    @staticmethod
    def ground_state(num_qubits: int) -> "QState":
        """Return the ground state .

        :param num_qubits: [description]
        :type num_qubits: int
        :return: [description]
        :rtype: QState
        """
        state = QState(np.array([1, 0] + [0 for i in range(2**num_qubits - 2)]), num_qubits)
        return state

    def __str__(self) -> str:
        return "-".join([f"{x:b}".zfill(self.length) for x in self.patterns])

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
