#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:55:00
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 15:58:57
"""


class PureState:

    # function to check if x is power of 2
    def isPowerOfTwo( x ):
    
        # First x in the below expression is
        # for the case when x is 0
        return x and (not(x & (x - 1)))
    
    # function to check whether the two numbers
    # differ at one bit position only
    def differAtOneBitPos( a , b ):
        return PureState.isPowerOfTwo(a ^ b)

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

    def __lt__(self, other: object) -> bool:
        return self.state < other.state

    def to_string(self, num_qubits: int = None) -> str:
        if num_qubits is None:
            return str(self)
        else:
            assert isinstance(num_qubits, int)
            return f"{self.state:0{num_qubits}b}"

    def flip(self, index: int) -> None:
        return PureState(self.state ^ (1 << index))

    def set0(self, index: int) -> None:
        return PureState(self.state & (~(1 << index)))

    def set1(self, index: int) -> None:
        return PureState(self.state | (1 << index))

    def count_ones(self) -> int:
        return bin(self.state).count("1")
    
    def is_adjacent(self, other: object) -> bool:
        return PureState.differAtOneBitPos(self.state, other.state)
    
def find_first_diff_qubit_index(state1: PureState, state2: PureState):

    return (state1.state ^ state2.state).bit_length() - 1