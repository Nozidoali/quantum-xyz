#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-17 22:24:18
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 02:25:07
"""

import numpy as np
from typing import List
from xyz.qstate import QState
from xyz.circuit import QCircuit, QBit

from .window_resyn import *

def resynthesis(circuit: QCircuit) -> QCircuit:
    """
    Extract windows from the given circuit
    The idea is similar to rip-up and reroute in VLSI design. We extract windows from the circuit and resynthesize each window to minimize the number of CNOTs.

    TODO: maximize the size of each window
    """

    windows = extract_windows_naive(circuit)
    new_circuit = QCircuit(circuit.get_num_qubits())

    for target_qubit, window, state_begin, state_end in windows:
        
        n_cnots_old = sum((g.get_cnot_cost() for g in window))
        
        new_window = resynthesize_window(state_begin, state_end, target_qubit, window)
        
        n_cnots_new = sum((g.get_cnot_cost() for g in new_window))
        
        print(f"n_cnots_old: {n_cnots_old}, n_cnots_new: {n_cnots_new}")
        new_circuit.add_gates(new_window)

    return new_circuit
