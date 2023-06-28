#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-28 10:35:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 10:55:33
'''

from typing import Any
from .StateSynthesisBase import *
from .QState import *

from typing import List

class SparseStateSynthesis(StateSynthesisBase):

    def __init__(self, target_state) -> None:
        StateSynthesisBase.__init__(self, target_state)


def synthesis_sparse_state(state: QState):
    pass