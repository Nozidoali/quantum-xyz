#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 15:56:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 22:57:44
"""

from Algorithms import *
from scipy.stats import unitary_group
import random

num_tests = 100


def test_zyz():

    for _ in range(num_tests):

        matrix = unitary_group.rvs(2)
        # matrix = np.array([[1, 1], [1, -1]]) * np.sqrt(0.5)
        # matrix = BasicGate.rz( random.random() * 2 * np.pi )
        # random_value = random.random() * np.pi
        # matrix = BasicGate.rz(random_value)

        alpha, beta, gamma = unitary_zyz_decomposition_legacy(matrix)

        new_matrix = BasicGate.rz(alpha) @ BasicGate.ry(beta) @ BasicGate.rz(gamma)
        # new_matrix = BasicGate.rz(gamma) @ BasicGate.ry(beta) @ BasicGate.rz(alpha)

        if not np.allclose(matrix, new_matrix):
            # print(random_value)
            print(matrix)
            print(new_matrix)
            print(alpha, beta, gamma)
            pass

        assert np.allclose(to_special_unitary(matrix), to_special_unitary(new_matrix), atol=2e-1)
