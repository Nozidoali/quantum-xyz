#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 16:31:47
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:20:23
'''

from .Operators import *

class QTransitionBase:

    def __init__(self, num_qubits: int) -> None:

        self.num_qubits = num_qubits
        
        self.__operators = [None]
        
        self.__states = [ground_state(num_qubits)]

    def add_operator(self, operator: QOperator) -> None:
        self.__operators.append(operator)

    def add_transition(self, state_before: QState, operator: QOperator, state_after: QState) -> None:
        self.__operators.append(operator)
        self.__states.append(state_after)


        if self.num_transitions == 0:
            self.__states[0] = state_before

    def add_transition_to_front(self, state_before: QState, operator: QOperator, state_after: QState) -> None:
        self.__operators.insert(1, operator)
        self.__states.insert(1, state_after)

        self.__states[0] = state_before

    def add_transition_to_back(self, state_before: QState, operator: QOperator, state_after: QState) -> None:
        return self.add_transition(state_before, operator, state_after)

    def num_transitions(self) -> int:
        return len(self.__operators) - 1
    
    def transition_at(self, index: int) -> QOperator:
        assert index >= 0 and index < self.num_transitions()

        state_before = self.__states[index]
        state_after = self.__states[index + 1]
        operator = self.__operators[index + 1]

        return state_before, operator, state_after
    
    def __add__(self, other: "QTransitionBase") -> None:
        
        assert self.num_qubits == other.num_qubits
        new_transition = QTransitionBase(self.num_qubits)
        
        new_transition.__operators = self.__operators + other.__operators[1:]
        new_transition.__states = self.__states + other.__states[1:]

        return new_transition
    
    def all_transitions(self) -> list:
        for i in range(self.num_transitions()):
            yield self.transition_at(i)