#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:43:30
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:15:29
"""

from typing import Any, List
import numpy as np

from .pure_state import PureState

def quantize(state_array: np.ndarray, num_qubits: int) -> np.ndarray:
    """
    Quantize an array of states into a smaller number of states using a specified number of qubits.
    @param state_array - the array of states to be quantized
    @param num_qubits - the number of qubits to use for quantization
    @return The quantized states
    """
    quantized_states = []

    for i in range(2**num_qubits):
        if state_array[i] != 0:
            curr_state = 0
            for j in range(num_qubits):
                if (i >> j) & 1 == 1:
                    curr_state |= 1 << j

            quantized_states.append(curr_state)

    return quantized_states

class QState:
    """The class method for the QState class .
    """
    def __init__(
        self, state_array: np.ndarray, num_qubits: int, is_quantized: bool = True
    ) -> None:
        self.num_qubits = num_qubits
        if not is_quantized:
            state_array = quantize(state_array, num_qubits)
        self.state_array = {PureState(x) for x in state_array}

    def copy(self) -> Any:
        """Return a copy of this QState .

        :return: [description]
        :rtype: Any
        """
        state_array = [int(x) for x in self.state_array]
        return QState(state_array, self.num_qubits, True)

    def count_ones(self) -> dict:
        """Count the number of times each one is one .

        :return: [description]
        :rtype: dict
        """
        one_count = {}
        for pivot_qubit in range(self.num_qubits):
            num_ones: int = 0
            for pure_state in self.state_array:
                if (int(pure_state) >> pivot_qubit) & 1 == 1:
                    num_ones += 1
            one_count[pivot_qubit] = num_ones

        return one_count

    def num_supports(self) -> int:
        """Returns the number of bits that are satisfied by the pure gates .

        :return: [description]
        :rtype: int
        """
        num_supports = 0

        for pivot_qubit in range(self.num_qubits):
            array = list(self.state_array)

            curr_value = (int(array[0]) >> pivot_qubit) & 1

            for pure_state in array[1:]:
                if (int(pure_state) >> pivot_qubit) & 1 != curr_value:
                    num_supports += 1
                    break

        return num_supports

    def get_num_qubits(self) -> int:
        """Returns the number of qubits in the model .

        :return: [description]
        :rtype: int
        """
        return self.num_qubits

    def __str__(self) -> str:
        return "-".join([f"{x:b}" for x in self.state_array])

    def __len__(self) -> int:
        return len(self.state_array)

    def __copy__(self) -> Any:
        return QState(self.state_array.copy(), self.num_qubits)

    def __call__(self) -> Any:
        for state in self.state_array:
            yield state

    def add_pure_state(self, pure_state: PureState) -> None:
        """Adds a pure state to the state_array .

        :param pure_state: [description]
        :type pure_state: PureState
        """
        self.state_array.add(pure_state)
        return

    def __lt__(self, other: Any) -> bool:
        sorted_self = sorted(self.state_array)
        sorted_other = sorted(other.state_array)
        for i in range(len(sorted_other)):
            if i >= len(sorted_self):
                return True
            if sorted_self[i] < sorted_other[i]:
                return True
            elif sorted_self[i] > sorted_other[i]:
                return False

        return False

    def __iter__(self) -> Any:
        sorted_self = sorted(list(self.state_array))
        return sorted_self.__iter__()

    def get_sorted_state_array(
        self, key=None, reverse: bool = False
    ) -> List[PureState]:
        """Returns a list of the state arrays sorted by key .

        :param key: [description], defaults to None
        :type key: [type], optional
        :param reverse: [description], defaults to False
        :type reverse: bool, optional
        :return: [description]
        :rtype: List[PureState]
        """
        return sorted(list(self.state_array), key=key, reverse=reverse)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, QState):
            return False

        if len(self) != len(__value):
            return False

        sorted_self = sorted(self.state_array)
        sorted_other = sorted(__value.state_array)

        for i in range(len(self)):
            if sorted_self[i] != sorted_other[i]:
                return False

        return True

    def __hash__(self) -> int:
        sorted_self = sorted(self.state_array)
        return hash(tuple(sorted_self))

def ground_state(num_qubits: int) -> QState:
    """
    Create a ground state of a specified number of qubits.
    @param num_qubits - the number of qubits
    @return The ground state
    """
    return QState([0], num_qubits)
