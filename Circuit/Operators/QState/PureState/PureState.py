#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 11:55:00
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 13:13:28
'''

class PureState:

    def __init__(self, state: int) -> None:
        self.state = state

    def __int__(self):
        return int(self.state)
    
    def __str__(self) -> str:
        return f"{self.state:b}"
    
    def __eq__(self, __value: object) -> bool:
        return self.state == __value.state
    
    def __hash__(self) -> int:
        return hash(self.state)
    
    def to_string(self, num_qubits: int = None) -> str:
        if num_qubits is None:
            return str(self)
        else:
            return f"{self.state:0{num_qubits}b}"
        
    def flip(self, index: int) -> None:
        return PureState(self.state ^ (1 << index))
    
    def set0(self, index: int) -> None:
        return PureState(self.state & (~(1 << index)))
    
    def set1(self, index: int) -> None:
        return PureState(self.state | (1 << index))