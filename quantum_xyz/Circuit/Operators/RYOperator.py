#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:23:59
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:32:04
"""

from .QOperatorBase import *
from .QuantizedRotation import *


class RYOperator(QOperatorBase):
    def __init__(self, num_qubits: int) -> None:
        super().__init__(num_qubits)
