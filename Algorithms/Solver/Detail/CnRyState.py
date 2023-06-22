#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 17:22:13
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 18:05:32
'''

from typing import List
import numpy as np

class CnRyState:

    def __init__(self, states: List[int] = [0], num_controls: int = 0) -> None:
        self.states = set(states[:]) # deep copy
        self.cost = num_controls

    def __lt__(self, other) -> bool:
        return self.cost < other.cost
    
    def __hash__(self) -> int:
        return hash(self.__str__())

    def __str__(self) -> str:
        sorted_states = sorted(list(self.states))
        return "-".join([f"{state:b}" for state in sorted_states])

    def __eq__(self, __value: object) -> bool:
        return self.__str__() == __value.__str__()
    
    def __len__(self) -> int:
        return len(self.states)

def to_cnry_state(state: np.ndarray) -> CnRyState:

    num_qubits = int(np.log2(len(state)))
    cnry_states = []

    for i in range(2 ** num_qubits):
        
        if state[i] != 0:

            curr_state = 0
            for j in range(num_qubits):
                if (i >> j) & 1 == 1:
                    curr_state |= (1 << j)
        
            cnry_states.append(curr_state)

    return CnRyState(cnry_states)
    