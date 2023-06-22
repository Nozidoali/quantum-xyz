#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 19:58:35
'''

from .Base import *
from typing import List

import numpy as np

class CRY(RotationGate, BasicGate, ControlledGate):

    def __init__(self, theta: float, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        
        BasicGate.__init__(self, QGateType.CRY, target_qubit)
        RotationGate.__init__(self, theta)
        ControlledGate.__init__(self, control_qubit, phase)