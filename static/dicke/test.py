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
    circuit = xyz.prepare_dicke_state(4, 2, map_gates=False)
    print(xyz.to_qiskit(circuit))
    circuit = xyz.resynthesis(circuit, verbose_level=3)
    print(xyz.to_qiskit(circuit))

    # now we measure the distance between the target state and the actual state
    state_vector_act = xyz.simulate_circuit(circuit)
    print("actual state: ", xyz.quantize_state(state_vector_act))
