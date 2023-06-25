#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-19 12:25:04
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 12:49:23
"""

import numpy as np
from Algorithms import *


def test_cofactor_decomposition():
    # matrix = np.array([0, 1, 1, 0, 1, 0, 0, 0])
    matrix = np.array([1, 0, 0, 0, 1, 0, 0, 0])

    cofactor_decomposition(matrix)

    pass
