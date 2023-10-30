#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-15 13:22:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-15 13:30:56
"""

from xyz.qstate.qstate import QState


def get_difference(state1: QState, state2: QState):
    """Returns the difference between two states .

    :param state1: [description]
    :type state1: QState
    :param state2: [description]
    :type state2: QState
    :return: [description]
    :rtype: [type]
    """

    diff_index_1 = {}
    diff_index_2 = {}
    diff_weights = {}

    for index in state1.index_to_weight:
        if index not in state2.index_to_weight:
            diff_index_1[index] = state1.index_to_weight[index]
        elif state1.index_to_weight[index] != state2.index_to_weight[index]:
            diff: float = state1.index_to_weight[index] - state2.index_to_weight[index]
            if diff >= 1e-6:
                diff_index_1[index] = diff

    for index in state2.index_to_weight:
        if index not in state1.index_to_weight:
            diff_index_2[index] = state2.index_to_weight[index]

    return diff_index_1, diff_index_2, diff_weights
