#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""
Author: Hanyu Wang
Created time: 2024-05-21 15:03:13
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-21 15:14:18
"""

import xyz

if __name__ == "__main__":
    state_vector = [
        1,
        1,
        1,
        -1,
        1,
        1,
        -1,
        1,
        1,
        1,
        1,
        1,
        -1,
        -1,
        -1,
        -1,
    ]
    state = xyz.quantize_state(state_vector)
    param = xyz.StatePreparationParameters(
        enable_exact_synthesis=True, n_qubits_max=100
    )
    circuit = xyz.prepare_state(state, param=param, verbose_level=0)
    new_circuit = xyz.resynthesis(circuit)
    state_vector_act = xyz.simulate_circuit(new_circuit)

    qc = xyz.to_qiskit(new_circuit)
    print(qc)
    print("target state: ", xyz.quantize_state(state_vector))
    print("actual state: ", xyz.quantize_state(state_vector_act))
