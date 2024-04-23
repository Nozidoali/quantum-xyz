#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-10 19:24:34
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-10 22:25:33
"""

import numpy as np

from xyz.circuit import CX
from xyz.circuit import X, RY
from xyz.circuit import QCircuit
from xyz.circuit import QState

ENABLE_Y_REDUCTION = True


def support_reduction(circuit: QCircuit, state: QState, enable_cnot: bool = True):
    """Apply the reduction to the circuit .

    :param circuit: [description]
    :type circuit: QCircuit
    :param state: [description]
    :type state: QState
    """

    # for collisions
    signature_to_qubits = {}

    signatures = state.get_qubit_signatures()
    const1 = state.get_const1_signature()

    gates = []

    new_state = QState(state.index_to_weight, state.num_qubits)

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

    if ENABLE_Y_REDUCTION:
        signatures = new_state.get_qubit_signatures()

        for qubit_index, signature in enumerate(signatures):
            # let us check the Y gate
            theta: float = None
            for index, _ in new_state.index_to_weight.items():
                reversed_index = index ^ (1 << qubit_index)
                if reversed_index not in new_state.index_to_weight:
                    theta = None
                    break

                index0 = index & ~(1 << qubit_index)
                index1 = index | (1 << qubit_index)

                weight0 = new_state.index_to_weight[index0]
                weight1 = new_state.index_to_weight[index1]

                _theta = 2 * np.arctan(weight1 / weight0)

                if theta is None:
                    theta = _theta
                elif np.isclose(theta, _theta):
                    continue
                else:
                    theta = None
                    break

            if theta is not None:
                # we can use the Y gate
                gate = RY(theta, circuit.qubit_at(qubit_index))
                gates.append(gate)
                new_state = gate.conjugate().apply(new_state)

    return new_state, gates[::-1]
