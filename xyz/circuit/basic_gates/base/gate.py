#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-20 18:44:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:55:41
"""

from enum import Enum, auto

from .qubit import QBit


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
    """Class method for creating a new gate class ."""

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


class BasicGate(QGate):
    """Class method for creating a gate .

    :param QGate: [description]
    :type QGate: [type]
    """

    def __init__(self, qgate_type: QGateType, target_qubit: QBit) -> None:
        QGate.__init__(self, qgate_type)

        if not isinstance(target_qubit, QBit):
            print(f"WARNING: target_qubit {target_qubit} is not a QBit")

        assert isinstance(target_qubit, QBit)
        self.target_qubit: QBit = target_qubit


class AdvancedGate(QGate):
    """Class method that creates a AdvancedGate class .

    :param QGate: [description]
    :type QGate: [type]
    """

    def __init__(self, qgate_type: QGateType) -> None:
        QGate.__init__(self, qgate_type)
