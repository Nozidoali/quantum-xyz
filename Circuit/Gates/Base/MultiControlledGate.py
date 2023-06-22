#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 19:40:46
'''

import numpy as np
from typing import List

from .QGate import *
from .QBit import *


class MultiControlledGate:

    def __init__(self, control_qubits: List[QBit], phases: List[int]) -> None:
        self.control_qubits = control_qubits
        self.phases = phases

    def has_zero_controls(self) -> bool:
        return len(self.control_qubits) == 0
    
    def has_one_control(self) -> bool:
        return len(self.control_qubits) == 1