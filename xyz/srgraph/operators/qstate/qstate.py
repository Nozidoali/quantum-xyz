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
from functools import cache

import copy
import numpy as np

from xyz.utils.timer import call_with_global_timer

__representative_cache = {}
__representative_cache_hit = 0

@cache
def representative_cache_hit():
    """Return the number of cache hits."""
    global __representative_cache_hit
    return __representative_cache_hit

@cache
def representative_cache_clear():
    """Clear the cache."""
    global __representative_cache
    __representative_cache = {}
    
@cache
def representative_cache_size():
    """Return the size of the cache."""
    global __representative_cache
    return len(__representative_cache)

@cache
def representative_cache_read(state: "QState") -> "QState":
    """Return the representative of the given state .

    :param state: [description]
    :type state: [type]
    :return: [description]
    :rtype: [type]
    """
    global __representative_cache
    global __representative_cache_hit
    if state in __representative_cache:
        __representative_cache_hit += 1
        return __representative_cache[state]
    else:
        return None

@cache
def representative_cache_write(state: "QState", value: "QState") -> None:
    """Write the representative of the given state .

    :param state: [description]
    :type state: [type]
    :param value: [description]
    :type value: [type]
    """
    global __representative_cache
    __representative_cache[state] = value

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

    def __transpose(self) -> List[int]:
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
        values = self.__transpose()
        values = set(values)
        self.length = len(values)
        self.const_one = (1 << self.length) - 1
        self.patterns = [0 for i in range(self.num_qubits)]
        for _, value in enumerate(values):
            for j in range(self.num_qubits):
                self.patterns[j] = self.patterns[j] << 1 | (value >> j & 1)

    def all_column_permutations(self, disable: bool = False):
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
            if disable:
                break

    @call_with_global_timer
    def representative(self) -> "QState":
        """Return a repr string for this object ."""
        
        cached_repr = representative_cache_read(self)
        if cached_repr is not None:
            return copy.deepcopy(cached_repr)
        
        repr_state = copy.deepcopy(self)

        # remove redundant columns, update length
        repr_state.cleanup_columns()

        for patterns in repr_state.all_column_permutations():
            # run x and qubit permutations
            for qubit_index in range(repr_state.num_qubits):
                # apply X gate to reduce pattern
                if patterns[qubit_index] >> (self.length - 1) == 1:
                    patterns[qubit_index] = ~patterns[qubit_index] & self.const_one

            # sort patterns
            patterns = sorted(patterns)

            # check if this is the smallest
            is_smallest = True
            for i in range(repr_state.num_qubits):
                if patterns[i] > repr_state.patterns[i]:
                    is_smallest = False
                    break
                if patterns[i] < repr_state.patterns[i]:
                    break

            # update if this is the smallest
            if is_smallest:
                repr_state.patterns = copy.deepcopy(patterns)
                
        representative_cache_write(self, repr_state)

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
        for pattern in sorted(self.patterns):
            ret_val <<= self.signature_length
            pattern = pattern & self.const_one
            
            if pattern > (~pattern & self.const_one):
                pattern = ~pattern & self.const_one

            ret_val |= pattern
        return hash(ret_val)
