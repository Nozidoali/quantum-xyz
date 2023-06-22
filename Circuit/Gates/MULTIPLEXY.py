#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 23:55:57
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 00:13:28
'''

from .Base import *
from typing import List

import numpy as np

class MULTIPLEXY(AdvancedGate):

    def __init__(self, theta0: float, theta1: float, control_qubit: QBit, target_qubit: QBit) -> None:

        AdvancedGate.__init__(self, QGateType.MULTIPLEX_Y)

        assert isinstance(target_qubit, QBit)
        assert isinstance(control_qubit, QBit)

        self.target_qubit: QBit = target_qubit
        self.control_qubit: QBit = control_qubit
        self.theta0: float = theta0
        self.theta1: float = theta1
        

    def __str__(self) -> str:
        control_str = '+'.join([str(qubit) + f"[{phase}]" for qubit, phase in zip(self.control_qubits, self.phases)])
        return f"MUXY({self.theta:0.02f}, {control_str})"