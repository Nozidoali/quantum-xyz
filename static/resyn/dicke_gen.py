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
    write_qasm,
    D_state,
)
from xyz import StatePreparationParameters as Param

import pandas as pd

if __name__ == "__main__":
    # for m_state in [n_qubits, 2**(n_qubits-1)]:
    for n_qubits in range(3, 20):
        state_vector = D_state(n_qubits, int(n_qubits / 2))
        target_state = quantize_state(state_vector)

        # synthesize the state
        with stopwatch("synthesis") as timer_old:
            param = Param(
                enable_exact_synthesis=False,
                enable_qubit_reduction=True,
                enable_cardinality_reduction=False,
            )
            circuit = prepare_state(
                target_state, map_gates=True, verbose_level=3, param=param
            )
            n_cnot_old = circuit.get_cnot_cost()

            write_qasm(circuit, f"dicke_{n_qubits}.qasm")
