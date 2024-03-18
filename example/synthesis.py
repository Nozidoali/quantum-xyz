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
    QCircuit,
    quantize_state,
    simulate_circuit,
    D_state,
    stopwatch,
    rand_state,
    prepare_state
)

if __name__ == "__main__":
    state_vector = rand_state(5, 4, uniform=False)

    # target_state = quantize_state(state_vector)
    target_state = quantize_state("0.29*|00001> + 0.61*|00111> + 0.53*|01100> + 0.52*|11111>")

    # synthesize the state
    with stopwatch("synthesis") as timer:
        circuit = prepare_state(target_state, map_gates=True, verbose_level=3)
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(state_vector_act - state_vector)

    print(circuit.to_qiskit())
    print("target state: ", quantize_state(target_state))
    print("actual state: ", quantize_state(state_vector_act))
