#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:46:01
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 10:57:47
"""

from .QStateBase import *
from typing import List
import numpy as np

class QStateFramed(QStateBase):
    def __init__(self, state_array: List[PureState], num_qubits: int) -> None:
        QStateBase.__init__(self, state_array)
        self.num_qubits = num_qubits

    def __str__(self) -> str:
        return "-".join([x.to_string(self.num_qubits) for x in self.state_array])

    def count_ones(self) -> dict:
        one_count = {}
        for pivot_qubit in range(self.num_qubits):
            num_ones: int = 0
            for pure_state in self.state_array:
                if (int(pure_state) >> pivot_qubit) & 1 == 1:
                    num_ones += 1
            one_count[pivot_qubit] = num_ones

        return one_count
    
    def column_at(self, column_index: int, control_phase: bool = True) -> int:
        ret_val: int = 0
        for row_index, pure_state in enumerate(self.state_array):
            phase = ((int(pure_state) >> column_index) & 1) == 1
            
            if phase == control_phase:
                ret_val |= row_index
            
        return ret_val
    
    def column_count_ones(self, column_index: int) -> int:
        ret_val: int = 0
        for row_index, pure_state in enumerate(self.state_array):
            ret_val += ((int(pure_state) >> column_index) & 1)
            
        return ret_val
    
    def column_is_mixed(self, column_index: int) -> bool:
        if len(self.state_array) <= 2:
            return False
        prev_val: int = None
        for pure_state in self.state_array:
            curr_val = ((int(pure_state) >> column_index) & 1)
            
            if prev_val == None:
                prev_val = curr_val
            
            else:
                if prev_val != curr_val:
                    return True
        
        return False

    def num_supports(self) -> int:
        num_supports = 0

        for pivot_qubit in range(self.num_qubits):
            array = list(self.state_array)

            curr_value = (int(array[0]) >> pivot_qubit) & 1

            for pure_state in array[1:]:
                if (int(pure_state) >> pivot_qubit) & 1 != curr_value:
                    num_supports += 1
                    break

        return num_supports
