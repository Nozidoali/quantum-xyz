#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-16 17:06:22
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-17 00:55:53
"""

# pylint: disable=wrong-import-position
# pylint: skip-file

import numpy as np

from xyz import (
    exact_cnot_synthesis,
    heuristic_cnot_synthesis,
    QCircuit,
    quantize_state,
    simulate_circuit,
    D_state,
    cnot_synthesis,
    print_green,
    stopwatch,
)

if __name__ == "__main__":
    # state_vector_exp = np.array([np.sqrt(2), 0, 1, 1])
    # state_vector_exp = np.array([1, 1, 1, 1, 1, 1, 3, 5])
    # state_vector_exp = np.array([1, 1, 1, 1, 1, 1, 3, 5, 1, 2, 2, 1, 1, 1, 3, 5])
    # state_vector_exp = np.array(np.sqrt([1, 2, 3, 0, 0, 3, 2, 1]))
    state_vector_exp = np.array(np.sqrt([2, 6, 8, 0, 0, 4, 3, 1]))
    # state_vector_exp = np.array([0, 1, 1, 0])
    # state_vector_exp = np.array([0, 0, 0, 0, 1, 0, 1, 1])
    # state_vector_exp = np.array([1, 0, 1, 1])
    # state_vector_exp = np.array([1, 1, 2, 0])
    # state_vector_exp = np.array([1, 1, 1, 2])
    # state_vector_exp = np.array([1, -2])

    # state_vector_exp = D_state(5, 2)
    # state_vector_exp = D_state(4, 1)

    state = quantize_state(state_vector_exp)

    circuit = QCircuit(state.num_qubits, map_gates=True)

    with stopwatch("exact_cnot_synthesis") as t:
        gates = exact_cnot_synthesis(circuit, state, verbose_level=1)

    print_green(f"synthesis: {t.time():0.02f} seconds")

    circuit.add_gates(gates)

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit).data
    dist = np.linalg.norm(state_vector_act - state_vector_exp)

    print("target state: ", state)
    print("actual state: ", quantize_state(state_vector_act))

    circ = circuit.to_qiskit()
    print(circ)
