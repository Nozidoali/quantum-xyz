#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-04-25 17:33:17
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-27 03:50:55
'''

import numpy as np
import xyz

if __name__ == "__main__":
    # state_vector = xyz.QBA_state(6, 33)
    state_vector = xyz.QBA_state(4, 9)
    target_state = xyz.quantize_state(state_vector)
    
    # synthesize the state
    with xyz.stopwatch("synthesis", verbose=True) as timer:
        param = xyz.StatePreparationParameters(
            enable_compression=False,
            enable_m_flow=False,
            enable_n_flow=True,
            enable_exact_synthesis=False,
        )
        circuit = xyz.prepare_state(target_state, map_gates=True, param=param)
        
    n_cnot = circuit.get_cnot_cost()
    # circuit = xyz.resynthesis(circuit, verbose_level=2)
    
    # now we measure the distance between the target state and the actual state
    state_vector_act = xyz.simulate_circuit(circuit)
    dist = np.linalg.norm(abs(state_vector_act) - abs(state_vector))

    qc = xyz.to_qiskit(circuit)
    print(qc)
    print("target state: ", xyz.quantize_state(state_vector))
    print("actual state: ", xyz.quantize_state(state_vector_act))
    assert dist < 1e-6

    print(xyz.to_tikz(circuit))