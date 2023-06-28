#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 15:21:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 18:06:35
"""

from Algorithms import *
from StatePreparator import *

num_qubits = 4
state = QState(D_state(num_qubits, 1), num_qubits)

print(state)

SparseStateSynthesis(state).run()
