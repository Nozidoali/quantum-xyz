#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-20 16:23:29
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-20 17:38:55
"""

import xyz


def run_bqskit(state_vector_begin, state_vector_end):
    from bqskit import compile
    from bqskit.qis import StateVector
    from bqskit.qis import StateSystem
    from bqskit.ext.qiskit import bqskit_to_qiskit
    from bqskit.ir.lang.qasm2 import OPENQASM2Language

    system = StateSystem(
        {StateVector(state_vector_begin): StateVector(state_vector_end)}
    )
    c = compile(system, optimization_level=3)
    qc_opt = bqskit_to_qiskit(c)
    n_cnot = qc_opt.count_ops().get("cx", 0)
    return n_cnot, qc_opt


if __name__ == "__main__":
    n_attempts: int = 0
    while True:
        print(f"Attempt {n_attempts}")
        n_attempts += 1

        state_vector = xyz.rand_state(2, 3, uniform=True)
        circuit = xyz.prepare_state(state_vector)
        windows = xyz.extract_windows_naive(circuit)
        for target_qubit, window, state_begin, state_end in windows:
            new_window = xyz.resynthesize_window(
                target_qubit, window, state_begin, state_end
            )
            n_cnot = sum((gate.get_cnot_cost() for gate in new_window))

            # if n_cnot < 2:
            #     continue

            state_vector_begin = state_begin.to_vector()
            state_vector_end = state_end.to_vector()

            n_cnot_new, qc_opt = run_bqskit(state_vector_begin, state_vector_end)

            from qiskit import transpile

            qc_opt = transpile(qc_opt, basis_gates=["cz", "ry", "rx", "rz", "x"])

            if n_cnot_new < n_cnot:
                print(f"state begin: {state_begin}")
                print(f"state end: {state_end}")
                print(qc_opt)
                for gate in new_window:
                    print(gate)
                exit(0)
            else:
                print(f"state begin: {state_begin}")
                print(f"state end: {state_end}")
                print(f"Failed: {n_cnot_new} >= {n_cnot}")
