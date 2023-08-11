#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""

from xyz.Circuit import *


class StateSynthesisBase:
    def __init__(self, target_state: QStateBase) -> None:
        self.target_state = target_state
        self.num_qubits = target_state.num_qubits

    def run(self) -> None:
        raise NotImplementedError
