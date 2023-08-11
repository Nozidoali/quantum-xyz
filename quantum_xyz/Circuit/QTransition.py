#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 16:33:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:21:23
"""

from quantum_xyz.Circuit.QTransitionBase import QTransitionBase
from .Operators import *
from .QTransitionWithSimulation import *


class QTransition(QTransitionWithSimulation):
    def __init__(self, num_qubits: int) -> None:
        QTransitionWithSimulation.__init__(self, num_qubits)

    def __add__(self, other: "QTransition") -> None:
        assert self.num_qubits == other.num_qubits

        new_transition = QTransition(self.num_qubits)

        for transition in self.all_transitions():
            new_transition.add_transition(*transition)

        for transition in other.all_transitions():
            new_transition.add_transition(*transition)

        return new_transition
