#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 11:55:00
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 12:01:06
'''

class PureState:

    def __init__(self, state: int) -> None:
        self.state = state

    def __int__(self):
        return int(self.state)
    
    def __str__(self) -> str:
        return f"{self.state:b}"
    
    def to_string(self, num_qubits: int = None) -> str:
        if num_qubits is None:
            return str(self)
        else:
            return f"{self.state:0{num_qubits}b}"