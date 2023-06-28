#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 10:38:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 10:56:52
'''

import numpy as np

class QStateBase:

    def __init__(self, state_array: np.ndarray) -> None:
        self.state_array = state_array

    def __str__(self) -> str:
        return '-'.join([f"{x:b}" for x in self.state_array])