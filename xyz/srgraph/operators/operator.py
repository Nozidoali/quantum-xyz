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
    """A method to set the operator type for the QOperatorType .

    :param Enum: [description]
    :type Enum: [type]
    """

    MCRY = auto()
    X = auto()
    CX = auto()
    T0 = auto()
    T1 = auto()
    CT0 = auto()
    CT1 = auto()


class QOperator:
    """Class method to create a QOperator class ."""

    def __init__(self, operator_type: QOperatorType) -> None:
        self.operator_type = operator_type


class QOperatorBase:
    """Class method to create a QOperatorBase subclass ."""

    def __init__(self, operator_type: QOperatorType, target_qubit_index: int) -> None:
        self.operator_type = operator_type
        self.target_qubit_index = target_qubit_index
