#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 13:11:53
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 14:53:20
'''

from .Base import *

from typing import List

class CX(BasicGate, ControlledGate):

    def __init__(self, control_qubit: QBit, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledGate.__init__(self, control_qubit)
    