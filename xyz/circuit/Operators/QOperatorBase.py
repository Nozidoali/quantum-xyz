#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:21:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:40:13
"""

from typing import Any
from .QOperator import *


class QOperatorBase:
    def __init__(self, type: QOperatorType, target_qubit_index: int) -> None:
        self.type = type
        self.target_qubit_index = target_qubit_index

    def __str__(self) -> str:
        raise NotImplementedError

    def __len__(self) -> int:
        return self.num_qubits

    def __copy__(self) -> Any:
        raise NotImplementedError
