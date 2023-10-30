#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-09 14:34:48
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-09 14:41:40
"""


from xyz.circuit import X
from xyz.circuit import QCircuit
from xyz.qstate import QState


def ground_state_calibration(circuit: QCircuit, state: QState):
    """Calculates the ground state calibration .

    :param circuit: [description]
    :type circuit: QCircuit
    :param state: [description]
    :type state: QState
    """

    assert state.get_sparsity() == 1

    # get the basis state
    index = list(state.index_set)[0]

    gates = []

    # get the 1s in the index
    for qubit in range(state.num_qubits):
        if index & (1 << qubit) != 0:
            gates.append(X(circuit.qubit_at(qubit)))

    return gates
