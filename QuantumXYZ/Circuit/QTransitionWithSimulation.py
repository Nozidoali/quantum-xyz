#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 16:35:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:05:46
'''

from .Operators import *
from .QTransitionQuantized import *

class QTransitionWithSimulation(QTransitionQuantized):

    def __init__(self, num_qubits: int) -> None:
        QTransitionQuantized.__init__(self, num_qubits)