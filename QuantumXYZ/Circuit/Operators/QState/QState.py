#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:43:30
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:15:29
"""

from typing import Any
import numpy as np
from .QStateQuantized import *


class QState(QStateQuantized):
    def __init__(self, state_array: np.ndarray, num_qubits: int, is_quantized: bool = True) -> None:
        QStateQuantized.__init__(self, state_array, num_qubits, is_quantized)

