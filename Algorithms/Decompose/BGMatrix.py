#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 16:00:17
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 17:31:43
'''

import numpy as np
from scipy.linalg import solve

def find_thetas(alphas):
    size = len(alphas)
    # for the gray code matrix
    M = np.zeros((size, size))
    for i in range(size):
        for j in range(size):

            #  The exponent is the bit-wise inner product of the binary vectors for the standard binary code representation of the integer i (bi) and the binary representation of the i th value of the gray code up to a value of 2) The j th value of the gray code is calculated using the bit-wise XOR of the unsigned binary j and a single shift right of the value of j , like so: ”j XOR (j>>1)” for C++ code

            bitwise_inner_product = bin(i & (j ^ (j >> 1))).count('1')
            M[i, j] = (-1) ** bitwise_inner_product
    
    thetas = solve(M, alphas)

    return thetas


