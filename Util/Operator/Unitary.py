#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 15:39:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 15:41:45
'''

import numpy as np

def to_unitary(matrix: np.ndarray):
    
    # for each column, orthogonalize it with the previous columns
    for i in range(matrix.shape[1]):
        for j in range(i):
            matrix[:, i] -= np.dot(matrix[:, j], matrix[:, i]) * matrix[:, j]
        matrix[:, i] /= np.linalg.norm(matrix[:, i])
    
    return matrix