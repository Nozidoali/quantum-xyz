#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:26:49
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:32:52
"""

from typing import List


class ControlledOperator:
    def __init__(self, control_qubit_index: int, control_qubit_phase: bool) -> None:
        self.control_qubit_index: int = control_qubit_index
        self.control_qubit_phase: bool = control_qubit_phase
