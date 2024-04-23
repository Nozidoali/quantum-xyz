#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-21 12:51:01
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-21 12:59:21
"""

from typing import List

import numpy as np
from xyz.circuit import QState


def get_ry_angles(state: QState, qubit_index: int) -> List[float]:
    """Return the projection of the state ."""
    thetas = []
    for idx in state.index_set:
        idx0 = idx & ~(1 << qubit_index)
        idx1 = idx0 ^ (1 << qubit_index)

        # check if the qubit is 1
        if idx == idx1:
            if idx0 not in state.index_set:
                thetas.append(np.pi)
            continue

        if idx1 not in state.index_set:
            thetas.append(0)
            continue

        # now we check the rotation angle
        weight_from = state.index_to_weight[idx0]
        weight_to = state.index_to_weight[idx1]
        _theta = 2 * np.arctan2(weight_to, weight_from)

        thetas.append(_theta)

    return thetas


def get_rotation_table(state: QState, qubit_index: int) -> dict:
    """Return the projection of the state .

    The keys in the dictionary are the indices (we make sure that all the values of pivot qubit is 0 in the indices)
    The values in the dictionary are the rotation angles

    :param qubit_index: the target qubit index (the pivot)
    :type qubit_index: int
    :return: the dictionary
    :rtype: dict
    """
    thetas = {}
    for idx in state.index_set:
        idx0 = idx & ~(1 << qubit_index)
        idx1 = idx0 ^ (1 << qubit_index)

        # check if the qubit is 1
        if idx == idx1:
            if idx0 not in state.index_set:
                thetas[idx0] = np.pi
            continue

        if idx1 not in state.index_set:
            thetas[idx0] = 0
            continue

        # now we check the rotation angle
        weight_from = state.index_to_weight[idx0]
        weight_to = state.index_to_weight[idx1]
        _theta = 2 * np.arctan2(weight_to, weight_from)

        thetas[idx0] = _theta

    return thetas


def get_cry_angles(
    state: QState, control_qubit_index: int, target_qubit_index: int, phase: bool = True
) -> List[float]:
    """Return the projection of the state ."""
    thetas = {}
    for idx in state.index_set:
        idx0 = idx & ~(1 << target_qubit_index)
        idx1 = idx0 ^ (1 << target_qubit_index)

        # check if the qubit is 1
        if idx == idx1:
            if idx0 not in state.index_set:
                thetas[idx0] = np.pi
            continue

        if idx1 not in state.index_set:
            thetas[idx0] = 0
            continue

        # now we check the rotation angle
        weight_from = state.index_to_weight[idx0]
        weight_to = state.index_to_weight[idx1]
        _theta = 2 * np.arctan2(weight_to, weight_from)
        thetas[idx0] = _theta

    cry_thetas = []
    for idx, theta in thetas.items():
        rdx = idx ^ (1 << control_qubit_index)

        if (idx >> control_qubit_index) & 1 == phase:
            continue

        if rdx not in thetas:
            continue

        if np.isclose(theta, thetas[rdx]):
            continue
        # this is the axis to run reflection
        beta = (thetas[rdx] + theta) / 2

        # need to rotate to the |+> state to perform CX
        cry_thetas.append(np.pi / 2 - beta)

    return cry_thetas


def get_ap_ry_angles(state: QState, qubit_index: int) -> float:
    # let us check the RY gate
    theta: float = None
    for index, _ in state.index_to_weight.items():
        reversed_index = index ^ (1 << qubit_index)
        if reversed_index not in state.index_to_weight:
            theta = None
            break

        index0 = index & ~(1 << qubit_index)
        index1 = index | (1 << qubit_index)

        weight0 = state.index_to_weight[index0]
        weight1 = state.index_to_weight[index1]

        _theta = 2 * np.arctan(weight1 / weight0)

        if theta is None:
            theta = _theta
        elif np.isclose(theta, _theta):
            continue
        else:
            theta = None
            break

    return theta


def get_ap_cry_angles(
    state: QState, control_qubit_index: int, target_qubit_index: int, phase: bool = True
) -> float:
    # let us check the RY gate
    theta: float = None
    for index, _ in state.index_to_weight.items():
        if (index >> control_qubit_index) & 1 != phase:
            continue

        reversed_index = index ^ (1 << target_qubit_index)
        if reversed_index not in state.index_to_weight:
            theta = None
            break

        index0 = index & ~(1 << target_qubit_index)
        index1 = index | (1 << target_qubit_index)

        weight0 = state.index_to_weight[index0]
        weight1 = state.index_to_weight[index1]

        _theta = 2 * np.arctan(weight1 / weight0)

        if theta is None:
            theta = _theta
        elif np.isclose(theta, _theta):
            continue
        else:
            theta = None
            break

    return theta


def get_most_frequent_theta(state: QState, qubit_index: int) -> float:
    """Return the projection of the state .

    :param qubit_index: [description]
    :type qubit_index: int
    :return: [description]
    :rtype: List[float]
    """
    thetas = state.get_ry_angles(qubit_index)

    best_theta = None
    best_theta_count = 0

    curr_theta = None
    curr_theta_count = 0
    for theta in sorted(thetas):
        if curr_theta is None:
            curr_theta = theta
            curr_theta_count = 1

            best_theta = curr_theta
            best_theta_count = curr_theta_count
        elif np.isclose(theta, curr_theta):
            curr_theta_count += 1
        else:
            if curr_theta_count > best_theta_count:
                best_theta = curr_theta
                best_theta_count = curr_theta_count
            curr_theta = theta
            curr_theta_count = 1

    return best_theta
