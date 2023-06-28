#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-19 12:06:15
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 19:21:13
"""

from Algorithms import *
from QuantumXYZ.Utils import *

import random

num_test: int = 100


def test_mcry_gate():
    theta = random.random() * np.pi
    theta = 0.5 * np.pi

    controls = {1: False, 2: False}

    unitary_gate = AdvancedGate.mcry(theta, controls, 0, 3)
    print(unitary_gate)
