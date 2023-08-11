#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:24:32
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:41:03
"""

from enum import Enum, auto


class QuantizedRotationType(Enum):
    SWAP = auto()
    MERGE0 = auto()
    MERGE1 = auto()
    SPLIT0 = auto()
    SPLIT1 = auto()


class QuantizedRotation:
    def __init__(self, rotation_type: QuantizedRotationType) -> None:
        self.rotation_type = rotation_type
