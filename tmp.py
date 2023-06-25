#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-25 15:21:11
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 17:50:06
'''

from Algorithms import *
from StatePreparator import *

num_qubits = 5
state = D_state(num_qubits, 2)
database = CnRyDataBase(num_qubits)
database.construct(to_state_list(state))

database.lookup(to_state_list(state))