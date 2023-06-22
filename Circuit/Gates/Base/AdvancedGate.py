#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 00:08:56
'''

import numpy as np
from .QGate import *
from .QBit import *

from typing import List

class AdvancedGate(QGate):

    def __init__(self, type: QGateType) -> None:
        QGate.__init__(self, type)

