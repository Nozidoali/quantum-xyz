#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 08:36:42
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 09:14:59
"""

import copy
import numpy as np
from xyz.circuit import X, CX, QCircuit, QState


def x_reduction(circuit: QCircuit, state: QState, enable_cnot: bool = True):
    signatures = state.get_qubit_signatures()
    const1 = state.get_const1_signature()

    signature_to_qubits = {}

    gates = []
    new_state = copy.deepcopy(state)

    for qubit_index, signature in enumerate(signatures):
        # this is already not a support
        if signature == 0:
            continue

        # this is not a support if we use a X gate
        if signature == const1:
            gate = X(circuit.qubit_at(qubit_index))
            gates.append(gate)
            new_state = gate.apply(new_state)
            continue

        # this is not a support if we use a CNOT gate
        if enable_cnot and signature in signature_to_qubits:
            control_qubit = circuit.qubit_at(signature_to_qubits[signature])
            target_qubit = circuit.qubit_at(qubit_index)
            control_phase = True

            gate = CX(control_qubit, control_phase, target_qubit)
            gates.append(gate)
            new_state = gate.apply(new_state)
            continue

        # this is not a support if we use a CNOT gate
        if enable_cnot and signature ^ const1 in signature_to_qubits:
            control_qubit = circuit.qubit_at(signature_to_qubits[signature ^ const1])
            target_qubit = circuit.qubit_at(qubit_index)
            control_phase = False

            gate = CX(control_qubit, control_phase, target_qubit)
            gates.append(gate)
            new_state = gate.apply(new_state)
            continue

        signature_to_qubits[signature] = qubit_index

    return new_state, gates
