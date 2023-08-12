#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:55:00
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 15:58:57
"""


class PureState:
    """Class decorator for creating PureState .

    :return: [description]
    :rtype: [type]
    """

    # function to check if x is power of 2
    @staticmethod
    def _is_power_of_two(x: int):
        """Returns True if x is a power of two two - way .

        :param x: [description]
        :type x: [type]
        :return: [description]
        :rtype: [type]
        """
        # First x in the below expression is
        # for the case when x is 0
        return x and (not(x & (x - 1)))
    
    # function to check whether the two numbers
    # differ at one bit position only
    @staticmethod
    def differ_at_one_bit(a, b):
        """Checks if two bit positions are in one bit - of - bit .

        :param a: [description]
        :type a: [type]
        :param b: [description]
        :type b: [type]
        :return: [description]
        :rtype: [type]
        """
        return PureState._is_power_of_two(a ^ b)

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
        """Return a string representation of the state .

        :param num_qubits: [description], defaults to None
        :type num_qubits: int, optional
        :return: [description]
        :rtype: str
        """
        if num_qubits is None:
            return str(self)
        else:
            assert isinstance(num_qubits, int)
            return f"{self.state:0{num_qubits}b}"

    def flip(self, index: int) -> None:
        """Return a pure state with the given index .

        :param index: [description]
        :type index: int
        :return: [description]
        :rtype: [type]
        """
        return PureState(self.state ^ (1 << index))

    def set0(self, index: int) -> None:
        """Return a new state with the given index .

        :param index: [description]
        :type index: int
        :return: [description]
        :rtype: [type]
        """
        return PureState(self.state & (~(1 << index)))

    def set1(self, index: int) -> None:
        """Return a new state with the given index .

        :param index: [description]
        :type index: int
        :return: [description]
        :rtype: [type]
        """
        return PureState(self.state | (1 << index))

    def count_ones(self) -> int:
        """Return the number of records in the state .

        :return: [description]
        :rtype: int
        """
        return bin(self.state).count("1")
    
    def is_adjacent(self, other: object) -> bool:
        """Return True if the state is adjacent to this state .

        :param other: [description]
        :type other: object
        :return: [description]
        :rtype: bool
        """
        return PureState.differ_at_one_bit(self.state, other.state)
    
def find_first_diff_qubit_index(state1: PureState, state2: PureState):
    """Find the first diff bit between two states .

    :param state1: [description]
    :type state1: PureState
    :param state2: [description]
    :type state2: PureState
    :return: [description]
    :rtype: [type]
    """
    return (state1.state ^ state2.state).bit_length() - 1