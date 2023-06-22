#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 14:33:21
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:05:37
'''

from typing import List
from .Gates import *

from .QCircuitBase import *

class QCircuitOptimized(QCircuitBase):

    def __init__(self) -> None:
        super().__init__()
    
    def add_gate(self, gate: QGate) -> None:
        '''
        Add a gate to the circuit, with optimization
        '''
        match gate.type:

            case QGateType.RY:
                if gate.is_trivial():
                    return
                else:
                    super().add_gate(gate)
            case QGateType.MCRY:
                if gate.has_zero_controls():
                    reduced_gate = RY(gate.theta, gate.target_qubit)
                    super().add_gate(reduced_gate)
                else:
                    super().add_gate(gate)
            case _:
                super().add_gate(gate)
    
    def add_gates(self, gates: List[QGate]) -> None:
        '''
        Add a list of gates to the circuit, with optimization
        '''
        for gate in gates:
            self.add_gate(gate)