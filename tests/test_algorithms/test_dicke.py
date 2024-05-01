#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-18 18:02:05
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 19:12:39
"""

import numpy as np
import xyz

dicke_qsp_results: list = [
    (3,1,4),
    (4,1,7),
    (4,2,6),
    (5,1,10),
    (5,2,16),
    (6,1,13),
    (6,2,22),
    (6,3,25)
]

def test_dicke(n_qubits: int, k: int, golden: int):
    state_vector = xyz.D_state(n_qubits, k)
    dicke_qsp_results.append({
        "num_qubits": n_qubits,
        "k": k,
        "state_vector": state_vector
    })
    print(f"n_qubits: {n_qubits}, k: {k}")
    with xyz.stopwatch("resynthesis") as timer_new:
        # DATE24
        param = xyz.StatePreparationParameters(
            enable_exact_synthesis=True,
            n_qubits_max=100
        )
        new_circuit = xyz.prepare_state(state_vector, map_gates=True, verbose_level=0, param=param)
    n_cnot_new = new_circuit.get_cnot_cost()
    state_vector_act = xyz.simulate_circuit(new_circuit)
    assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    print(xyz.to_qiskit(new_circuit))
    print(f"n_cnot_new: {n_cnot_new}")
    if n_cnot_new != golden:
        print(f"n_qubits: {n_qubits}, k: {k}, n_cnot_new: {n_cnot_new}, golden: {golden}")
    # assert n_cnot_new == golden

def test_qsp_dicke():
    for n, k, golden in dicke_qsp_results:
        test_dicke(n, k, golden)
        
if __name__ == "__main__":
    # test_qsp_dicke()
    test_dicke(6, 2, 22)