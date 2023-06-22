#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 14:14:19
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:01:37
'''

from qiskit.circuit.library.standard_gates import *
from qiskit import QuantumCircuit
from ..Gates.Base.QGate import *
from ..Gates import *

import numpy as np


class SpecialGates:

    def mcry(gate: MCRY):

        num_control_qubits = len(gate.control_qubits)

        # we need to reverse the order of the control qubits
        # because the qiskit's control gate is in the reverse order
        control_str = ''.join([str(int(phase)) for phase in gate.phases])[::-1]
        
        return RYGate(gate.theta).control(
            num_control_qubits, 
            ctrl_state=control_str)
