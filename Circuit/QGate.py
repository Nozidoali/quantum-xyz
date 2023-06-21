#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-20 18:44:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-20 18:46:34
'''

from enum import Enum, auto

class QGateType(Enum):
    CY = auto()
    CZ = auto()
    CX = auto()

    NONE = auto()
    

class QGate:

    def __init__(self) -> None:
        self.type = QGateType.NONE

    def __str__(self) -> str:
        return self.type.name
    
    