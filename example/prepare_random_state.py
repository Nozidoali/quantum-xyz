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
    rand_state,
    quantize_state,
    prepare_state,
    stopwatch,
    simulate_circuit,
    resynthesis,
    to_qiskit,
)
from xyz import StatePreparationParameters as Param

if __name__ == "__main__":
    # state_vector = rand_state(4, 6, uniform=False)
    state_vector = np.array(
        [
            0.16382266,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.38105493,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.43878958,
            0.0,
            0.0,
            0.0,
            0.0,
            0.13652317,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.11894722,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.38323048,
            0.0,
            0.48973041,
            0.0,
            0.0,
            0.00112803,
            0.0,
            0.15454862,
            0.0,
            0.06307129,
            0.0,
            0.22988688,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.36772542,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
    )
    target_state = quantize_state(state_vector)

    # synthesize the state
    with stopwatch("synthesis", verbose=True) as timer:
        param = Param(
            enable_exact_synthesis=False,
            enable_n_flow=True,
            enable_m_flow=False,
        )
        circuit = prepare_state(
            target_state, map_gates=False, verbose_level=3, param=param
        )

        # circuit = resynthesis(circuit)

    exit(0)
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))
    assert dist < 1e-6

    qc = to_qiskit(circuit)
    print(qc)
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
