#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-30 20:03:27
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-30 20:17:40
'''

import numpy as np
from .QStateQuantized import *

class QStateCanonical(QStateQuantized):

    def __init__(self, state_array: np.ndarray, num_qubits: int, is_quantized: bool = True) -> None:
        QStateQuantized.__init__(self, state_array, num_qubits, is_quantized)

    def __str__(self) -> str:
        return "\n".join([x.to_string(self.num_qubits) for x in sorted(list(self.state_array))])
