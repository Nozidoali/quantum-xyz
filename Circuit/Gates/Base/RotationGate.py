#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 19:45:34
'''

import numpy as np

from .QGate import *
from .QBit import *

class RotationGate:

    def __init__(self, theta: float) -> None:
        self.theta = theta

    def is_trivial(self) -> bool:
        return np.isclose(self.theta, 0) or np.isclose(self.theta, 2 * np.pi)
    
    def is_pi(self) -> bool:
        return np.isclose(self.theta, np.pi)