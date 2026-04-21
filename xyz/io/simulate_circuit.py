#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""
Author: Hanyu Wang
Created time: 2023-09-13 12:02:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 12:04:42
"""

import numpy as np
from qiskit.quantum_info import Statevector

from xyz.circuit import QCircuit
from .to_qiskit import to_qiskit


def simulate_circuit(circuit: QCircuit) -> np.ndarray:
    """
    Simulate a circuit . This is a wrapper for qiskit
    Aer.get_backend("qasm_simulator").run(circuit).result().get_statevector()

    :param circuit: the quantum circuit to simulate
    :type circuit: QCircuit

    """

    state_vector = Statevector(to_qiskit(circuit)).data
    state_vector[np.abs(state_vector) < 1e-10] = 0

    return state_vector
