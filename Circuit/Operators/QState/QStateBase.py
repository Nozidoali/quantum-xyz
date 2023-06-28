#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:38:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:14:34
"""

import numpy as np
from typing import Any
from .PureState import *

class QStateBase:
    def __init__(self, state_array: np.ndarray) -> None:
        self.state_array = [PureState(x) for x in state_array]

    def __str__(self) -> str:
        return "-".join([f"{x:b}" for x in self.state_array])

    def __len__(self) -> int:
        return len(self.state_array)

    def __copy__(self) -> Any:
        return QStateBase(self.state_array.copy())
