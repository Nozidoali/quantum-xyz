#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-03-18 18:44:35
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 18:46:03
'''

import random
import numpy as np

from itertools import combinations

def rand_state(num_qubit: int, sparsity: int, uniform: bool = False):
    state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
        random.random() if not uniform else 1 for i in range(sparsity)
    ]
    np.random.shuffle(state_array)

    # normalize the state
    state_array = state_array / np.linalg.norm(state_array)

    return state_array

def place_ones(size, count):
    for positions in combinations(range(size), count):
        p = [0] * size
        for i in positions:
            p[i] = 1
        yield p

def all_states(num_qubit: int, sparsity: int):
    for perm in place_ones(2**num_qubit, sparsity):
        yield perm[:]