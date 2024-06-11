#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-06-11 21:29:55
Last Modified by: Hanyu Wang
Last Modified time: 2024-06-11 21:52:54
"""

import numpy as np
from xyz.circuit import QCircuit, CX, CRY, MCRY, X


def insert_scs(circuit: QCircuit, n: int, k: int, j: int, verbose_level: int = 0):
    """
    insert_scs insert the split and cyclic shift gates into the circuit.
    """
    assert k >= 1, "k should be greater than or equal to 1"
    theta = 2 * np.arccos(np.sqrt(1 / n))
    circuit.add_gate(CX(circuit.qubit_at(j + 1), True, circuit.qubit_at(j)))
    circuit.add_gate(CRY(theta, circuit.qubit_at(j), True, circuit.qubit_at(j + 1)))
    circuit.add_gate(CX(circuit.qubit_at(j + 1), True, circuit.qubit_at(j)))
    for i in range(1, k):
        if j + i + 1 >= circuit.get_num_qubits():
            break
        circuit.add_gate(CX(circuit.qubit_at(j + i + 1), True, circuit.qubit_at(j)))
        control_qubits = [circuit.qubit_at(j), circuit.qubit_at(j + i)]
        control_phases = [True, True]
        theta = 2 * np.arccos(np.sqrt((i + 1) / (n)))
        circuit.add_gate(
            MCRY(theta, control_qubits, control_phases, circuit.qubit_at(j + i + 1))
        )
        circuit.add_gate(CX(circuit.qubit_at(j + i + 1), True, circuit.qubit_at(j)))


def prepare_dicke_state(n: int, k: int, map_gates: bool = True, verbose_level: int = 0):
    circuit = QCircuit(n, map_gates=map_gates)

    # prepare seed
    for i in range(k):
        circuit.add_gate(X(circuit.qubit_at(i)))

    # prepare the dicke state
    for i in range(n - 1):
        insert_scs(circuit, n - i, k, i)

    return circuit
