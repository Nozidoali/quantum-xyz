#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-20 18:44:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:55:41
"""

from enum import Enum, auto


class QGateType(Enum):
    X = auto()
    Y = auto()
    Z = auto()

    CY = auto()
    CZ = auto()
    CX = auto()

    RX = auto()
    RY = auto()
    RZ = auto()

    CRY = auto()
    CRZ = auto()
    CRX = auto()

    MCRY = auto()

    MULTIPLEX_Y = auto()

    NONE = auto()


class QGate:
    def __init__(self, type: QGateType) -> None:
        self.type = type

    def __str__(self) -> str:
        return self.type.name

    def get_type(self) -> QGateType:
        return self.type