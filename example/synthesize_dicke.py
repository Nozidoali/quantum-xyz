#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-01-19 12:03:04
Last Modified by: Hanyu Wang
Last Modified time: 2024-01-19 12:05:07
"""

import numpy as np
from xyz import (
    D_state,
    quantize_state,
    prepare_state,
    stopwatch,
    simulate_circuit,
    resynthesis,
    to_qiskit,
)

if __name__ == "__main__":
    state_vector = D_state(4, 2)
    target_state = quantize_state(state_vector)

    # synthesize the state
    with stopwatch("synthesis", verbose=True) as timer:
        circuit = prepare_state(target_state, map_gates=True)
        circuit = resynthesis(circuit)
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))
    assert dist < 1e-6

    qc = to_qiskit(circuit)
    print(qc)
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
