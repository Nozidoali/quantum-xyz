#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-18 16:28:18
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 17:33:10
'''

import numpy as np

class BasicGate:
    def ry(theta):
        return np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]])

    def rz(theta):
        return np.array([[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]])

    def x():
        return np.array([[0, 1], [1, 0]])
    
    