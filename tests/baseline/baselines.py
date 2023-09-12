#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-08 13:40:10
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-10 14:32:59
"""

# pylint: skip-file

from math import ceil
import subprocess
import re
import random
import numpy as np
from IPython.display import Markdown, display
from qiskit import QuantumCircuit, QuantumRegister, transpile, Aer
from qclib.state_preparation import (
    MergeInitialize,
)

from qclib.util import build_state_dict


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

def run_dd_based_method(state: np.ndarray):

    cx = None

    # get the bit string
    state_str = "".join(["1" if x > 0 else "0" for x in state])
    with open("tmp.txt", "w") as f:
        f.write(state_str)
    # baseline
    subprocess.run(
        "qsp_using_sota tmp.txt > tmp.rpt",
        shell=True,
        stdout=subprocess.DEVNULL,
    )

    # get the number of cnot
    with open("tmp.rpt", "r") as f:
        for line in f:
            if "cnots" in line:
                cx = int(re.sub("[^0-9]", "", line))
                break
            
    return cx

def run_sparse_state_synthesis(state: np.ndarray):
    """Run the baseline pipeline .

    reference:

    https://github.com/qclib/qclib-papers/blob/main/examples/state_preparation_benchmark.ipynb


    :param state: [description]
    :type state: [type]
    """

    state_dict = build_state_dict_fixed(state)

    n_qubits = int(np.log2(len(state)))

    initialize = MergeInitialize.initialize

    circuit = QuantumCircuit(n_qubits)

    initialize(circuit, state_dict)

    # transpiled = transpile(circuit, basis_gates=["u", "cx", "cu"], optimization_level=3)
    # print(transpiled)

    transpiled = transpile(circuit, basis_gates=["u", "cx"], optimization_level=0)
    qubits = len(transpiled.qubits)
    depth = transpiled.depth()
    cx = transpiled.count_ops().get("cx", 0)

    backend = Aer.get_backend("qasm_simulator")
    transpiled.save_statevector()
    state_vector = backend.run(transpiled).result().get_statevector()
    

    assert np.allclose(state_vector, state), f"state vector is not correct, {state_vector} != {state}"

    return qubits, depth, cx
