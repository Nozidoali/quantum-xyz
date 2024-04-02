#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-04-02 13:06:12
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-02 14:36:34
'''

# pylint: skip-file
import numpy as np
from xyz.cxyz import initialize
from xyz import D_state, quantize_state, prepare_state, stopwatch, simulate_circuit, resynthesis

if __name__ == "__main__":
    state_vector = D_state(4, 2)
    target_state = quantize_state(state_vector)
    with stopwatch("py", verbose = True) as timer:
        circuit = prepare_state(target_state, map_gates=True)
    # verify
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(state_vector_act - state_vector)

    qc = circuit.to_qiskit()
    # print(circuit.to_qiskit())
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))


    with stopwatch("c", verbose = True) as timer:
        circuit = initialize(target_state)
    n_cnot = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(state_vector_act - state_vector)

    qc = circuit.to_qiskit()
    # print(circuit.to_qiskit())
    print("target state: ", quantize_state(state_vector))
    print("actual state: ", quantize_state(state_vector_act))
