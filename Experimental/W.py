#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-21 11:18:01
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-21 11:21:52
"""

from Circuit import *
from Algorithms import *
from StatePreparator import *
import numpy as np


def prepare_w_state(num_qubits: int):
    circuit = QCircuit(num_qubits)

    state = W_state(num_qubits)

    decision_tree = get_decision_tree_from_state(state)
