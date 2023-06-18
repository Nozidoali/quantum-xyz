#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 14:46:55
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 14:49:07
"""

import numpy as np
from scipy.linalg import det

def to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    """Convert gate tensor to the special unitary group."""
    rank = matrix.shape[0]
    matrix_ = matrix / det(matrix) ** (1 / rank)
    return matrix_
