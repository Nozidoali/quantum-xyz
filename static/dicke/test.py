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
    for n in range(4, 16):
        for k in range(1, n // 2 + 1):
            circuit = xyz.prepare_dicke_state(n, k, map_gates=True)
            # print(xyz.to_qiskit(circuit))
            circuit = xyz.resynthesis(circuit, verbose_level=0)
            # print(xyz.to_qiskit(circuit))

            state_vector = xyz.D_state(n, k)

            # now we measure the distance between the target state and the actual state
            # state_vector_act = xyz.simulate_circuit(circuit)
            # print("actual state: ", xyz.quantize_state(state_vector_act))
            n_cnots = sum((g.get_cnot_cost() for g in circuit.get_gates()))
            print(f"n={n}, k={k}: cnot={n_cnots}")
