#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-25 12:02:57
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 12:03:53
'''

import numpy as np

def inverse(state: np.ndarray):
    boolean_state = state.astype(bool)
    boolean_state = np.logical_not(boolean_state)
    return boolean_state.astype(float) / np.sqrt(np.sum(boolean_state.astype(float) ** 2))