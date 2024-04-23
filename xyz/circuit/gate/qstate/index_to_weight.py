#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-15 13:31:48
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-15 13:37:33
"""


def index_to_str(index_to_weight: dict, num_qubits: int):
    """Prints the index_to_weight dictionary.

    :param index_to_weight: [description]
    :type index_to_weight: dict
    """

    index_str = ""

    if len(index_to_weight) == 0:
        return index_str

    if index_to_weight is None:
        return index_str

    assert isinstance(
        index_to_weight, dict
    ), f"index_to_weight must be a dictionary, got {type(index_to_weight)}"

    for index, weight in index_to_weight.items():
        index_str += f"{index:0{num_qubits}b}: {weight:0.02f}, "

    return index_str
