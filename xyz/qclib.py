#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-05 17:03:46
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-05 17:15:50
"""

import numpy as np
from qiskit import transpile
from qiskit import QuantumCircuit


def build_state_dict_fixed(state: np.ndarray):
    """
    Builds a dict of the non zero amplitudes with their
    associated binary strings as follows:
      { '000': <value>, ... , '111': <value> }
    Args:
      state: The classical description of the state vector
    """
    n_qubits = (np.log2(len(state))).astype(int)
    state_dict = {}
    for value_idx, value in enumerate(state):
        if value != 0:
            binary_string = f"{value_idx:0{n_qubits}b}"[::-1]
            state_dict[binary_string] = value
    return state_dict


def run_qclib(state: np.array):
    from qclib.state_preparation import LowRankInitialize, MergeInitialize

    state_dict = build_state_dict_fixed(state)

    n_qubits = int(np.log2(len(state)))

    circuit = QuantumCircuit(n_qubits)
    MergeInitialize.initialize(circuit, state_dict)

    transpiled = transpile(circuit, basis_gates=["u", "cx"], optimization_level=0)
    qubits = len(transpiled.qubits)
    depth = transpiled.depth()
    cx = transpiled.count_ops().get("cx", 0)
    return transpiled
