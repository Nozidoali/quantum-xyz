#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-08-20 12:48:10
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-20 13:54:22
'''

import copy
from functools import cache
from itertools import permutations

from xyz.utils.timer import call_with_global_timer
    

__REPR_CACHE = {}
__REPR_CACHE_HIT = 0

@cache
def representative_cache_hit():
    """Return the number of cache hits."""
    global __REPR_CACHE_HIT
    return __REPR_CACHE_HIT

@cache
def representative_cache_clear():
    """Clear the cache."""
    global __REPR_CACHE
    __REPR_CACHE = {}
    
@cache
def representative_cache_size():
    """Return the size of the cache."""
    global __REPR_CACHE
    return len(__REPR_CACHE)

@cache
def representative_cache_read(state: "QState") -> "QState":
    """Return the representative of the given state .

    :param state: [description]
    :type state: [type]
    :return: [description]
    :rtype: [type]
    """
    global __REPR_CACHE
    global __REPR_CACHE_HIT
    if state in __REPR_CACHE:
        __REPR_CACHE_HIT += 1
        return __REPR_CACHE[state]
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
    global __REPR_CACHE
    __REPR_CACHE[state] = value

def __all_column_permutations(state: "QState"):
    """Generator over all permutations of all columns in the DataFrame .

    :yield: [description]
    :rtype: [type]
    """
    values = state.transpose()
    for perm in permutations(values):
        # transpose back
        patterns = [0 for i in range(state.num_qubits)]
        for _, value in enumerate(perm):
            for j in range(state.num_qubits):
                patterns[j] = patterns[j] << 1 | (value >> j & 1)

        yield patterns
        
def __lowest_column_permutations(state: "QState"):
    """Get the smallest column permutations that are not equal to the given state .

    :return: [description]
    :rtype: [type]
    """
    values = state.transpose()
    sorted_values = sorted(values)
    return state.transpose_back(sorted_values)
    
@call_with_global_timer
def representative(self) -> "QState":
    """Return a repr string for this object ."""
    
    cached_repr = representative_cache_read(self)
    if cached_repr is not None:
        return copy.deepcopy(cached_repr)
    
    repr_state = copy.deepcopy(self)

    # remove redundant columns, update length
    repr_state.cleanup_columns()
    
    patterns = __lowest_column_permutations(repr_state)

    # run x and qubit permutations
    for qubit_index in range(repr_state.num_qubits):
        # apply X gate to reduce pattern
        if patterns[qubit_index] & 1 == 1:
            patterns[qubit_index] = ~patterns[qubit_index] & self.const_one

    repr_state.patterns = copy.deepcopy(patterns)
            
    representative_cache_write(self, repr_state)

    return repr_state

@call_with_global_timer
def representative_old(self) -> "QState":
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
