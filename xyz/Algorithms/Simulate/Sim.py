#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 20:07:14
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 20:08:00
"""

from xyz.circuit import *
from typing import List, Any


def simulate(circuit: QCircuit):
    if not isinstance(circuit, QCircuit):
        simulator = Aer.get_backend("qasm_simulator")
        result = execute(circuit, backend=simulator, shots=2**14).result()
        return result.get_counts(circuit)

    else:
        circ = circuit.to_qiskit()
        simulator = Aer.get_backend("qasm_simulator")
        result = execute(circ, backend=simulator, shots=2**14).result()
        return result.get_counts(circ)
