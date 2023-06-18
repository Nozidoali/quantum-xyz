#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 16:11:54
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 16:14:59
'''

import numpy as np
from scipy import stats

def random_operator(num_qubits: int) -> np.ndarray:

    return stats.unitary_group.rvs(2**num_qubits)