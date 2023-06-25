#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 13:19:49
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 15:04:48
"""


from typing import List
import numpy as np


class CnRyCanonicalState:
    def __init__(self, states: List[int] = [0]) -> None:
        self.states: set = set(list(states)[:])  # deep copy

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __str__(self) -> str:
        sorted_states = sorted(list(self.states))
        return "-".join([f"{state:b}" for state in sorted_states])

    def __eq__(self, __value: object) -> bool:
        return self.__str__() == __value.__str__()

    def __len__(self) -> int:
        return len(self.states)
