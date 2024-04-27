#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-04-25 19:58:23
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-25 20:08:00
'''

import numpy as np

from .qstate import QState

def is_equal(qstate1: QState, qstate2: QState) -> bool:
    """
    is_equal:
    return True if the two states are equal
    """
    for index, weight in qstate1.index_to_weight.items():
        if index not in qstate2.index_to_weight:
            return False
        if not np.isclose(weight, qstate2.index_to_weight[index]):
            return False
        
    for index, weight in qstate1.index_to_weight.items():
        if index not in qstate1.index_to_weight:
            return False
        if not np.isclose(weight, qstate1.index_to_weight[index]):
            return False
        
    return True