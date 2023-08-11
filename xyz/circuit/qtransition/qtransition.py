#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 16:33:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:21:23
"""

from .operators import QOperator, QState, ground_state

class QTransition:
    """Class method to call the transition class ."""

    def __init__(self, num_qubits: int) -> None:
        """Initialize the circuit .

        :param num_qubits: [description]
        :type num_qubits: int
        """
        self.num_qubits = num_qubits

        self.__operators = [None]

        self.__states = [ground_state(num_qubits)]

    def add_operator(self, operator: QOperator) -> None:
        """Adds an operator to the list of operators .

        :param operator: [description]
        :type operator: QOperator
        """
        self.__operators.append(operator)

    def add_transition(
        self, state_before: QState, operator: QOperator, state_after: QState
    ) -> None:
        """Adds a transition to the state .

        :param state_before: [description]
        :type state_before: QState
        :param operator: [description]
        :type operator: QOperator
        :param state_after: [description]
        :type state_after: QState
        """
        if self.num_transitions() == 0:
            self.__states[0] = state_before

        self.__operators.append(operator)
        self.__states.append(state_after)

    def add_transition_to_front(
        self, state_before: QState, operator: QOperator, state_after: QState
    ) -> None:
        """Adds a transition to the front of the list .

        :param state_before: [description]
        :type state_before: QState
        :param operator: [description]
        :type operator: QOperator
        :param state_after: [description]
        :type state_after: QState
        """
        self.__operators.insert(1, operator)
        self.__states.insert(1, state_after)

        self.__states[0] = state_before

    def add_transition_to_back(
        self, state_before: QState, operator: QOperator, state_after: QState
    ) -> None:
        """Adds a transition to the given state before the given state .

        :param state_before: [description]
        :type state_before: QState
        :param operator: [description]
        :type operator: QOperator
        :param state_after: [description]
        :type state_after: QState
        :return: [description]
        :rtype: [type]
        """
        return self.add_transition(state_before, operator, state_after)

    def num_transitions(self) -> int:
        """The number of transitions in the chain .

        :return: [description]
        :rtype: int
        """
        return len(self.__operators) - 1

    def transition_at(self, index: int) -> QOperator:
        """Returns the state before the given index .

        :param index: [description]
        :type index: int
        :return: [description]
        :rtype: QOperator
        """
        assert index >= 0 and index < self.num_transitions()

        state_before = self.__states[index]
        state_after = self.__states[index + 1]
        operator = self.__operators[index + 1]

        return state_before, operator, state_after

    def all_transitions(self) -> list:
        """Return a list of all transitions in the state .

        :return: [description]
        :rtype: list
        :yield: [description]
        :rtype: Iterator[list]
        """
        for i in range(self.num_transitions()):
            yield self.transition_at(i)

    def __add__(self, other: "QTransition") -> None:
        """Adds the two QTransition to this QTransition .

        :param other: [description]
        :type other: QTransition
        :return: [description]
        :rtype: [type]
        """
        assert self.num_qubits == other.num_qubits

        new_transition = QTransition(self.num_qubits)

        for transition in self.all_transitions():
            new_transition.add_transition(*transition)

        for transition in other.all_transitions():
            new_transition.add_transition(*transition)

        return new_transition
