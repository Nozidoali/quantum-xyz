#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:09:23
'''

import numpy as np
from typing import List

from .QGate import *
from .QBit import *


class ControlledGate:

    def __init__(self, control_qubit: QBit, phase: int = 1) -> None:
        self.phase = phase
        
        assert isinstance(control_qubit, QBit)
        self.control_qubit = control_qubit

