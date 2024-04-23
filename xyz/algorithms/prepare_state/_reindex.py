#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-22 21:53:17
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-22 21:55:27
"""

from xyz.circuit import QState
from xyz.circuit import QCircuit


def reindex_circuit(circuit: QCircuit, state: QState) -> tuple:
    """
    reindex_circuit:
    reindex the circuit
    """
    # compact the state
    # now we get the sub state and sub circuit:
    sub_index_to_weight = {}
    old_to_new_qubit_mapping = {}

    supports = state.get_supports()
    num_supports = len(supports)
    for new_index, old_index in enumerate(supports):
        old_to_new_qubit_mapping[old_index] = new_index
    for index, weight in state.index_to_weight.items():
        new_index: int = 0
        for i, support in enumerate(supports):
            if index & (1 << support) != 0:
                new_index |= 1 << i
        sub_index_to_weight[new_index] = weight
    state = QState(sub_index_to_weight, num_supports)
    circuit = circuit.sub_circuit(supports)

    return state, circuit
