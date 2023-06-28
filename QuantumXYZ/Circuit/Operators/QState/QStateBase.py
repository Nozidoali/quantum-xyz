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
    def __init__(self, state_array: np.ndarray = []) -> None:
        self.state_array: set = set([PureState(x) for x in state_array])

    def __str__(self) -> str:
        return "-".join([f"{x:b}" for x in self.state_array])

    def __len__(self) -> int:
        return len(self.state_array)

    def __copy__(self) -> Any:
        return QStateBase(self.state_array.copy())

    def __call__(self) -> Any:
        
        for state in self.state_array:
            yield state

    def add_pure_state(self, pure_state: PureState) -> None:
        self.state_array.add(pure_state)
        return 
    
    def __lt__(self, other: Any) -> bool:
        return False
    
    def __iter__(self) -> Any:
        return self.state_array.__iter__()