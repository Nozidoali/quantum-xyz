#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 15:49:27
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-11 23:56:48
"""

from qiskit import QuantumCircuit, transpile

import numpy as np

import xyz

state_vector = xyz.D_state(4, 2)

circuit_qiskit = QuantumCircuit(4)
circuit_qiskit.initialize(state_vector, [0, 1, 2, 3])
circuit_qiskit_transpiled = transpile(circuit_qiskit, basis_gates=["cx", "ry", "u"], optimization_level=3)

print(circuit_qiskit_transpiled)
print(circuit_qiskit_transpiled.count_ops())


quantized_state = xyz.quantize_state(state_vector)
circuit = xyz.cnot_synthesis(quantized_state)

circuit = circuit.to_qiskit()
circuit = transpile(circuit, basis_gates=["cx", "ry", "u"], optimization_level=0)

print(circuit)
print(circuit.count_ops())
