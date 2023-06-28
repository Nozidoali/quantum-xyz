#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 10:58:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 10:59:07
'''

from Algorithms.Synthesis.QState import QStateBase
from .StateSynthesisBase import *

class SearchBasedStateSynthesis(StateSynthesisBase):
    
    def __init__(self, target_state: QStateBase) -> None:
        StateSynthesisBase.__init__(self, target_state)
