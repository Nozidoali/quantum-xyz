#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 15:57:09
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 16:38:06
'''

from Algorithms import *

num_tests = 10

def test_muxiplier():

    # identity matrix
    c1 = np.array([[1, 0], [0, 0]])
    c2 = np.array([[0, 0], [0, 1]])

    u1 = random_operator(1)
    u2 = random_operator(1)

    matrix = np.kron(c1, u1) + np.kron(c2, u2)
    
    # print(matrix)

    D, V, W = decompose_uniformly_controlled_gate(matrix)

    V_matrix = np.kron( np.identity(2), V )
    W_matrix = np.kron( np.identity(2), W )
    D_matrix = np.kron( c1, D ) + np.kron( c2, D.conj().T )

    print(matrix)
    print(V_matrix @ D_matrix @ W_matrix)

    assert np.allclose( V_matrix @ D_matrix @ W_matrix, matrix)