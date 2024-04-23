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
    QCircuit,
    quantize_state,
    simulate_circuit,
    D_state,
    stopwatch,
    rand_state,
    prepare_state,
    resynthesis,
    read_qasm,
    to_qiskit,
)

import pandas as pd
from xyz import StatePreparationParameters as Param

if __name__ == "__main__":
    n_qubits = 4

    state_vector = D_state(n_qubits, int(n_qubits / 2))
    target_state = quantize_state(state_vector)
    param = Param(
        enable_exact_synthesis=False,
        enable_n_flow=True,
        enable_m_flow=False,
    )
    circuit = prepare_state(target_state, map_gates=True, verbose_level=3, param=param)

    # circuit = read_qasm("./benchmarks/dicke_6.qasm")

    # print(to_qiskit(circuit))

    # now we measure the distance between the target state and the actual state
    state_vector_exp = simulate_circuit(circuit)

    n_cnots = circuit.get_cnot_cost()
    print("n_cnots: ", n_cnots)

    new_circuit = resynthesis(circuit)
    n_cnots_new = new_circuit.get_cnot_cost()
    print("n_cnots_new: ", n_cnots_new)

    state_vector_act = simulate_circuit(new_circuit)
    print("expect state: ", quantize_state(state_vector_exp))
    print("actual state: ", quantize_state(state_vector_act))
