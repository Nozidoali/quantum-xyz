#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-13 12:02:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 12:04:42
"""

import numpy as np
from qiskit import Aer, transpile

from xyz.qstate import quantize_state
from xyz.utils.colors import print_yellow

from .qcircuit import QCircuit


def verify_circuit_and_count_cnot(circuit: QCircuit, state_vector_expect: np.ndarray, skip_verify: bool = False):
    """Verify that the given circuit is correct .

    :param circuit: [description]
    :type circuit: QCircuit
    :param state_vector_expect: [description]
    :type state_vector_expect: np.ndarray
    :raises ValueError: [description]
    """
    qiskit_circuit = circuit.to_qiskit()

    transpiled = transpile(
        qiskit_circuit, basis_gates=["u", "cx"], optimization_level=0
    )
    cx = transpiled.count_ops()["cx"] if "cx" in transpiled.count_ops() else 0

    if not skip_verify:
        backend = Aer.get_backend("qasm_simulator")
        transpiled.save_statevector()
        state_vector_actual = backend.run(transpiled).result().get_statevector()

        # normalize actual
        state_vector_actual = state_vector_actual / np.linalg.norm(state_vector_actual)
        state_vector_actual = abs(state_vector_actual.data)
        state_vector_expect = abs(state_vector_expect)

        if not np.allclose(state_vector_actual, state_vector_expect, atol=1e-2):
            print_yellow(
                f"state vector is not correct, expect {quantize_state(state_vector_expect)}, actual {quantize_state(state_vector_actual)}"
            )

    return cx
