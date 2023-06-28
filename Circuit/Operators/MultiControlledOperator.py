#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:27:44
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:29:03
"""

from typing import List
from .QState import *

class MultiControlledOperator:
    def __init__(
        self, control_qubit_indices: List[int], control_qubit_phases: List[bool]
    ) -> None:
        self.control_qubit_indices = control_qubit_indices
        self.control_qubit_phases = control_qubit_phases

    def is_controlled(self, pure_state: PureState) -> bool:
        
        for index, phase in zip(self.control_qubit_indices, self.control_qubit_phases):
            if (int(pure_state) >> index) & 1 != phase:
                return False
        
        return True
