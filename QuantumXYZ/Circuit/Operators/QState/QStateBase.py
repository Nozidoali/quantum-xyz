#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:38:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:14:34
"""

import numpy as np
from typing import Any, List
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
        sorted_self = sorted(self.state_array)
        sorted_other = sorted(other.state_array)
        for i in range(len(sorted_other)):
            if i >= len(sorted_self):
                return True
            if sorted_self[i] < sorted_other[i]:
                return True
            elif sorted_self[i] > sorted_other[i]:
                return False

        return False

    def __iter__(self) -> Any:
        sorted_self = sorted(list(self.state_array))
        return sorted_self.__iter__()
    
    def get_sorted_state_array(self, key, reverse: bool = False) -> List[PureState]:
        return sorted(list(self.state_array), key=key, reverse=reverse)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, QStateBase):
            return False

        if len(self) != len(__value):
            return False

        sorted_self = sorted(self.state_array)
        sorted_other = sorted(__value.state_array)

        for i in range(len(self)):
            if sorted_self[i] != sorted_other[i]:
                return False

        return True

    def __hash__(self) -> int:
        sorted_self = sorted(self.state_array)
        return hash(tuple(sorted_self))
