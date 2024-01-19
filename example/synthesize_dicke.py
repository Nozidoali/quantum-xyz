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
    hybrid_cnot_synthesis,
    stopwatch,
    HybridCnotSynthesisStatistics,
    simulate_circuit,
)


if __name__ == "__main__":
    state_vector = D_state(5, 1)
    target_state = quantize_state(state_vector)
    with stopwatch("synthesis") as timer:
        stats = HybridCnotSynthesisStatistics()
        circuit = hybrid_cnot_synthesis(target_state, map_gates=True, stats=stats)
    stats.report()
    cx = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit).data
    dist = np.linalg.norm(state_vector_act - state_vector)

    print(circuit.to_qiskit())
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
