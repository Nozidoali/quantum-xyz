#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-18 11:32:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-18 11:32:58
"""

from qiskit import *
from qiskit import Aer, execute
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from matplotlib import pyplot as plt
from qiskit.tools.visualization import plot_histogram

import numpy as np
from typing import List
from qiskit.circuit.library.standard_gates import *


from .Gates import *
from .QCircuitOptimized import *


class QCircuitParams:
    do_mapping: bool = True

    def set_mapping(do_mapping: bool):
        QCircuitParams.do_mapping = do_mapping


class QCircuit(QCircuitOptimized):
    def __init__(self, num_qubits):
        super().__init__()
        self.init_qubits(num_qubits)
        self.set_mapping(QCircuitParams.do_mapping)
