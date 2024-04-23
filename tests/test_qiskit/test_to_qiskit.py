#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 09:43:34
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 09:45:22
"""

import xyz


def test_to_qiskit():
    circuit = xyz.QCircuit(2)
    circuit.add_gate(xyz.X(circuit.qubit_at(0)))
    qc = xyz.to_qiskit(circuit)
    assert qc.num_qubits == 2
