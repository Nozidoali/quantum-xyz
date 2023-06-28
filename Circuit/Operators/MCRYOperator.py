#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 11:36:46
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:42:30
"""

from typing import Any
from .QOperatorBase import *
from .QuantizedRotation import *
from .MultiControlledOperator import *
from .QState import *

class MCRYOperator(QOperatorBase, QuantizedRotation, MultiControlledOperator):
    def __init__(
        self,
        target_qubit_index: int,
        rotation_type: QuantizedRotationType,
        control_qubit_indices: List[int],
        control_qubit_phases: List[bool],
    ) -> None:
        QOperatorBase.__init__(self, QOperatorType.MCRY, target_qubit_index)
        QuantizedRotation.__init__(self, rotation_type)
        MultiControlledOperator.__init__(
            self, control_qubit_indices, control_qubit_phases
        )

    def __call__(self, state: QState) -> Any:
        