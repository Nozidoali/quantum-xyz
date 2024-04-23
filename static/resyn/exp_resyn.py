#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-16 17:06:22
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-17 00:55:53
"""

# pylint: disable=wrong-import-position
# pylint: skip-file

import numpy as np

from xyz import (
    quantize_state,
    stopwatch,
    rand_state,
    prepare_state,
    resynthesis,
    simulate_circuit,
)
from xyz import StatePreparationParameters as Param

import pandas as pd

if __name__ == "__main__":
    N_TESTS = 1

    datas = []

    # for m_state in [n_qubits, 2**(n_qubits-1)]:
    for n_qubits in range(3, 10):
        # for m_state in [2 ** (n_qubits - 1)]:
        for m_state in [n_qubits]:
            for _ in range(N_TESTS):
                state_vector = rand_state(n_qubits, m_state, uniform=True)

                target_state = quantize_state(state_vector)
                # target_state = quantize_state("0.29*|00001> + 0.61*|00111> + 0.53*|01100> + 0.52*|11111>")

                # synthesize the state
                with stopwatch("synthesis") as timer_old:
                    circuit = prepare_state(
                        target_state, map_gates=True, verbose_level=0
                    )
                    n_cnot_old = circuit.get_cnot_cost()
                state_vector_act = simulate_circuit(circuit)
                print("target state: ", quantize_state(state_vector))
                print("actual state: ", quantize_state(state_vector_act))
                assert np.linalg.norm(state_vector_act - state_vector) < 1e-6

                with stopwatch("resynthesis") as timer_new:
                    circuit = resynthesis(circuit)
                    n_cnot_new = circuit.get_cnot_cost()

                state_vector_act = simulate_circuit(circuit)
                print("actual state: ", quantize_state(state_vector_act))
                assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
                data = {
                    "n_qubits": n_qubits,
                    "m_state": m_state,
                    "n_cnot_old": n_cnot_old,
                    "n_cnot_new": n_cnot_new,
                    "time_old": timer_old.time(),
                    "time_new": timer_new.time(),
                }

                datas.append(data)

                df = pd.DataFrame(datas)
                df.to_csv("resynthesis.csv")
