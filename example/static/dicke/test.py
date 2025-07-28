#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""
Author: Hanyu Wang
Created time: 2024-06-11 21:49:25
Last Modified by: Hanyu Wang
Last Modified time: 2024-06-11 21:51:45
"""

import xyz

if __name__ == "__main__":
    for n in range(6, 21):
        for k in range(1, 8):
            if n < k:
                continue
            circuit = xyz.prepare_dicke_state(n, k, map_gates=False)
            # print(xyz.to_qiskit(circuit))
            
            if k <= 2:
                circuit = xyz.resynthesis(circuit, verbose_level=0)
            # print(xyz.to_qiskit(circuit))

            # state_vector = xyz.D_state(n, k)
            # param = xyz.StatePreparationParameters(
            #     enable_exact_synthesis=True, n_qubits_max=100
            # )
            # circuit = xyz.prepare_state(
            #     state_vector, map_gates=True, verbose_level=0, param=param
            # )
            # print(xyz.to_qiskit(circuit))

            # now we measure the distance between the target state and the actual state
            # state_vector_act = xyz.simulate_circuit(circuit)
            # print("actual state: ", xyz.quantize_state(state_vector_act))
            n_cnots = sum((g.get_cnot_cost() for g in circuit.get_gates()))
            print(f"n={n}, k={k}: cnot={n_cnots}")
