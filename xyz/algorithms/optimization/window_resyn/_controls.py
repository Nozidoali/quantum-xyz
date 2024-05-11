#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-22 18:29:16
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-25 19:06:51
"""

import numpy as np
from typing import List


def get_candidate_controls(rotation_table: dict, num_qubits: int) -> List[int]:
    """
    get_candidate_controls:
    return the possible control qubits for the given rotation table:
    """
    selected = set()
    candidates = list(range(num_qubits))
    for index, theta in rotation_table.items():
        candidates_to_remove: set = set()
        for qubit_index in candidates:
            index_reversed = index ^ (1 << qubit_index)
            # this condition is buggy!
            if index_reversed not in rotation_table:
                continue
            theta_reversed: float = rotation_table[index_reversed]
            if np.isclose(theta, theta_reversed):
                continue
            selected.add(qubit_index)
            candidates_to_remove.add(qubit_index)
        for qubit_index in candidates_to_remove:
            candidates.remove(qubit_index)

    return list(selected)
