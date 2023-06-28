#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 10:42:43
'''

from .QState import *

class StateSynthesisBase:

    def __init__(self, target_state: QStateBase) -> None:
        self.target_state = target_state
    