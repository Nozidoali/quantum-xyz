#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-12 01:43:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-12 01:44:38
"""

from enum import Enum, auto


class QuantizedRotationType(Enum):
    """This class method is used to instantiate a Quantized RotationType object .

    :param Enum: [description]
    :type Enum: [type]
    """

    SWAP = auto()
    MERGE0 = auto()
    MERGE1 = auto()
    SPLIT0 = auto()
    SPLIT1 = auto()


class QuantizedRotation:
    """Classmethod to convert a QuantizedRotation to QuantizedRotation ."""

    def __init__(self, rotation_type: QuantizedRotationType) -> None:
        self.rotation_type = rotation_type
