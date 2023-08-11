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
    """This method is used to set the auto - gate type for QGate type .

    :param Enum: [description]
    :type Enum: [type]
    """
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
    """Class method for creating a new gate class .
    """
    def __init__(self, qgate_type: QGateType) -> None:
        self.qgate_type = qgate_type

    def __str__(self) -> str:
        return self.qgate_type.name

    def get_qgate_type(self) -> QGateType:
        """Returns the q gate type .

        :return: [description]
        :rtype: QGateType
        """
        return self.qgate_type
