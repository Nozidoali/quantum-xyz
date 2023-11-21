#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-16 17:06:22
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-17 00:55:53
"""

from tracemalloc import stop
import numpy as np

from xyz import exact_cnot_synthesis_opt, exact_cnot_synthesis
from xyz import QCircuit
from xyz import quantize_state
from xyz import simulate_circuit
from xyz import D_state
from xyz.utils.timer import stopwatch


if __name__ == "__main__":

    # state_vector_exp = np.array([np.sqrt(2), 0, 1, 1])
    # state_vector_exp = np.array([1, 1, 1, 1, 0, 0, 0, 5])
    # state_vector_exp = np.array([0, 1, 1, 0])
    # state_vector_exp = np.array([0, 0, 0, 0, 1, 0, 1, 1])
    # state_vector_exp = np.array([1, 0, 1, 1])
    # state_vector_exp = np.array([1, 1, 2, 0])
    # state_vector_exp = np.array([1, 1, 1, 2])
    # state_vector_exp = np.array([1, -2])

    state_vector_exp = D_state(4, 2)

    state = quantize_state(state_vector_exp)

    circuit = QCircuit(state.num_qubits, map_gates=True)

    with stopwatch("exact_cnot_synthesis") as t:
        gates = exact_cnot_synthesis(circuit, state, verbose_level=1)
        # gates = exact_cnot_synthesis_opt(circuit, state, verbose_level=1)
    print("exact_cnot_synthesis_opt: ", t.time())
    for gate in gates:
        circuit.add_gate(gate)

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit).data
    dist = np.linalg.norm(state_vector_act - state_vector_exp)

    print("target state: ", state)
    print("actual state: ", quantize_state(state_vector_act))

    circ = circuit.to_qiskit()
    print(circ)
