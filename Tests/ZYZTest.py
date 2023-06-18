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

    # identity matrix
    matrix = np.array([[1, 0], [0, 1]])
    alpha, beta, gamma = unitary_zyz_decomposition(matrix)
    assert alpha == 0 and beta == 0 and gamma == 0

    # RY(pi) matrix
    matrix = np.array([[0, -1], [1, 0]])
    alpha, beta, gamma = unitary_zyz_decomposition(matrix)
    assert alpha == 0 or alpha == 2 * np.pi
    assert beta == np.pi
    assert gamma == 0 or gamma == 2 * np.pi

    for _ in range(num_tests):

        matrix = unitary_group.rvs(2)
        # matrix = np.array([[0, -1], [1, 0]])
        # matrix = BasicGate.rz( random.random() * 2 * np.pi )
        random_value = random.random() * 2 * np.pi
        matrix = BasicGate.rz(random_value)

        alpha, beta, gamma = unitary_zyz_decomposition(matrix)

        new_matrix = BasicGate.rz(alpha) @ BasicGate.ry(beta) @ BasicGate.rz(gamma)

        if not np.allclose(matrix, new_matrix):
            print(random_value)
            print(alpha, beta, gamma)

        assert np.allclose(to_special_unitary(matrix), to_special_unitary(new_matrix))
