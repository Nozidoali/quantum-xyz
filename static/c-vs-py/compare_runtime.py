#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-02 13:06:12
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-02 14:56:07
"""

# pylint: skip-file
import numpy as np
import pandas as pd
from xyz.cxyz import initialize
from xyz import (
    D_state,
    quantize_state,
    prepare_state,
    stopwatch,
    simulate_circuit,
    resynthesis,
    StatePreparationParameters,
    rand_state,
)


def compare_runtime(state_vector: np.ndarray, verbose: bool = False):
    target_state = quantize_state(state_vector)
    with stopwatch("py", verbose=verbose) as timer_py:
        # circuit = prepare_state(target_state, map_gates=True, param=StatePreparationParameters(enable_m_flow=False, enable_n_flow=False, enable_progress_bar=False))
        circuit = prepare_state(
            target_state,
            map_gates=True,
            param=StatePreparationParameters(enable_progress_bar=False),
        )
    # verify
    n_cnot_py = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(state_vector_act - state_vector)

    qc = circuit.to_qiskit()
    # print(circuit.to_qiskit())
    if verbose:
        print("target state: ", quantize_state(state_vector))
        print("actual state: ", quantize_state(state_vector_act))

    with stopwatch("c", verbose=verbose) as timer_c:
        circuit = initialize(target_state)
    n_cnot_c = circuit.get_cnot_cost()

    # now we measure the distance between the target state and the actual state
    state_vector_act = simulate_circuit(circuit)
    dist = np.linalg.norm(state_vector_act - state_vector)

    qc = circuit.to_qiskit()
    # print(circuit.to_qiskit())
    if verbose:
        print("target state: ", quantize_state(state_vector))
        print("actual state: ", quantize_state(state_vector_act))

    data = {}
    data["py_time"] = timer_py.duration
    data["c_time"] = timer_c.duration
    data["py_cnot"] = n_cnot_py
    data["c_cnot"] = n_cnot_c
    data["speedup"] = timer_py.duration / timer_c.duration
    return data


if __name__ == "__main__":
    datas = []

    for i in range(100):
        num_qubits = 4
        cardinality = num_qubits
        state_vector = rand_state(num_qubits, cardinality, uniform=False)
        data = compare_runtime(state_vector, verbose=False)
        datas.append(data)

    avg_speedup = np.mean([data["speedup"] for data in datas])
    print(f"Average speedup: {avg_speedup}")

    df = pd.DataFrame(datas)
    df.to_csv("compare_runtime.csv", index=False)
