#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:34:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:35:15
"""

from enum import Enum, auto


class QOperatorType(Enum):
    MCRY = auto()


class QOperator:
    def __init__(self, type: QOperatorType) -> None:
        self.type = type
