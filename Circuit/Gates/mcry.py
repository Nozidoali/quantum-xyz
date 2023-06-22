#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 19:56:35
'''

from .Base import *
from typing import List

import numpy as np

class MCRY(RotationGate, BasicGate, MultiControlledGate):

    def __init__(self, theta: float, control_qubits: List[QBit], phases: List[int], target_qubit: QBit) -> None:
        
        BasicGate.__init__(self, QGateType.MCRY, target_qubit)
        RotationGate.__init__(self, theta)
        MultiControlledGate.__init__(self, control_qubits, phases)

    def __str__(self) -> str:
        control_str = '+'.join([str(qubit) for qubit in self.control_qubits])
        return f"MCRY({self.theta:0.02f}, {control_str})"