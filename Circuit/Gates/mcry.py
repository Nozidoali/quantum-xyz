#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 14:59:01
'''

from .Base import *
from typing import List

import numpy as np

class MCRY(RotationGate, BasicGate, MultiControlledGate):

    def __init__(self, theta: float, control_qubits: List[QBit], phases: List[int], target_qubit: QBit) -> None:
        
        BasicGate.__init__(self, QGateType.MCRY, target_qubit)
        RotationGate.__init__(self, theta)
        MultiControlledGate.__init__(self, control_qubits, phases)