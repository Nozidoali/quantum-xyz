#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-20 12:48:10
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-20 21:44:51
"""

import copy
from functools import cache
from itertools import permutations
from .qstate import QState, from_val

from xyz.utils.timer import call_with_global_timer


REPR_CACHE = {}
REPR_CACHE_HIT = 0


@cache
def representative_cache_hit():
    """Return the number of cache hits."""
    global REPR_CACHE_HIT
    return REPR_CACHE_HIT


@cache
def representative_cache_clear():
    """Clear the cache."""
    global REPR_CACHE
    REPR_CACHE = {}


@cache
def representative_cache_size():
    """Return the size of the cache."""
    global REPR_CACHE
    return len(REPR_CACHE)


@cache
def representative_cache_read(state: "QState") -> "QState":
    """Return the representative of the given state .

    :param state: [description]
    :type state: [type]
    :return: [description]
    :rtype: [type]
    """
    global REPR_CACHE
    global REPR_CACHE_HIT
    if state in REPR_CACHE:
        REPR_CACHE_HIT += 1
        return REPR_CACHE[state]
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
    global REPR_CACHE
    REPR_CACHE[state] = value


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


def precompute_representatives(num_qubits: int):
    """AI is creating summary for precompute_representatives

    :param num_qubits: [description]
    :type num_qubits: int
    :return: [description]
    :rtype: [type]
    """
    
    repr_table = [i for i in range(2 ** (2**num_qubits))]
    
    def find(a: int) -> int:
        """Find the representative of a."""
        if repr_table[a] != a:
            repr_table[a] = find(repr_table[a])
        return repr_table[a]

    def merge(a: int, b: int) -> None:
        """Merge two representatives."""
        a = find(a)
        b = find(b)
        if a < b:
            repr_table[b] = a
        else:
            repr_table[a] = b


    assert num_qubits <= 4  # otherwise too large

    # Pauli-X
    for i in range(2 ** (2**num_qubits)):
        if i == 0:
            continue  # 0 is not a valid state
        state = from_val(i, num_qubits)
        assert state.to_value() == i
        for qubit in range(num_qubits):
            new_state = state.apply_x(qubit)
            merge(i, new_state.to_value())

    # Pauli-Y
    for i in range(2 ** (2**num_qubits)):
        if i == 0:
            continue
        state = from_val(i, num_qubits)
        assert state.to_value() == i
        for qubit in range(num_qubits):
            if state.patterns[qubit] == 0 or state.patterns[qubit] == state.const_one:
                # apply split
                new_state = state.apply_split(qubit)
                merge(i, new_state.to_value())

    # Qubit Permutations
    for i in range(2 ** (2**num_qubits)):
        if i == 0:
            continue
        state = from_val(i, num_qubits)
        assert state.to_value() == i

        # apply qubit permutations
        patterns = state.patterns[:]
        for perm in permutations(range(num_qubits)):
            new_patterns = [0 for i in range(num_qubits)]
            for j in range(num_qubits):
                new_patterns[j] = patterns[perm[j]]
            new_state = QState(new_patterns, state.length)
            merge(i, new_state.to_value())

    # report the number of representatives
    num_representatives = 0
    num_repr_sparsity = {}
    num_state_sparsity = {}
    for i in range(2 ** (2**num_qubits)):
        if i == 0:
            continue
        sparsity = bin(i).count("1")
        if sparsity not in num_state_sparsity:
            num_state_sparsity[sparsity] = 0
        num_state_sparsity[sparsity] += 1
        if find(i) == i:
            num_representatives += 1
            if sparsity not in num_repr_sparsity:
                num_repr_sparsity[sparsity] = 0
            num_repr_sparsity[sparsity] += 1


def __lowest_column_permutations(state: "QState"):
    """Get the smallest column permutations that are not equal to the given state .

    :return: [description]
    :rtype: [type]
    """
    values = state.transpose()
    sorted_values = sorted(values)
    return state.transpose_back(sorted_values)


@call_with_global_timer
def representative(_state: QState) -> "QState":
    """Return a repr string for this object ."""

    state = copy.deepcopy(_state)

    # pre-processing
    state.cleanup_columns()

    # pre-processing Xs
    state = copy.deepcopy(state)
    x_signatures = state.get_x_signatures()
    for i in x_signatures:
        state = state.apply_x(i)

    # pre-processing Ys
    y_signatures = state.get_y_signatures()
    for i in y_signatures:
        state = state.apply_merge0(i)

    return state, x_signatures, y_signatures


@call_with_global_timer
def representative_old(state: QState) -> "QState":
    """Return a repr string for this object ."""

    cached_repr = representative_cache_read(state)
    if cached_repr is not None:
        return copy.deepcopy(cached_repr)

    repr_state = copy.deepcopy(state)

    # remove redundant columns, update length
    repr_state.cleanup_columns()

    all_patterns = list(__all_column_permutations(state))
    for i, _patterns in enumerate(all_patterns):
        patterns = _patterns[:]
        # run x and qubit permutations
        for qubit_index in range(repr_state.num_qubits):
            # apply X gate to reduce pattern
            if ~patterns[qubit_index] & state.const_one < patterns[qubit_index]:
                patterns[qubit_index] = ~patterns[qubit_index] & state.const_one

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

    representative_cache_write(state, repr_state)

    return repr_state
