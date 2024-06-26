#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-08 12:59:35
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-10 17:52:33
"""

import numpy as np

from xyz.circuit.gate.cx import CX
from xyz.circuit.gate.mcry import MCRY
from xyz.circuit.qcircuit import QCircuit

from xyz.circuit import QState
from .support_reduction import x_reduction


def _maximize_difference_once(state: QState, indices: set, diff_lit: dict):
    max_difference: int = -1

    best_index_set_0 = set()
    best_qubit = None
    best_value = None

    assert len(indices) >= 2
    length = len(indices)

    for qubit in range(state.num_qubits):
        # we cannot be better than this
        if max_difference == length - 1:
            break

        if qubit in diff_lit:
            continue

        index_set_0 = set()

        for index in indices:
            if index & (1 << qubit) == 0:
                index_set_0.add(index)

        length0 = len(index_set_0)
        difference = abs(length - (length0 << 1))

        # this means either the qubit is all 0 or all 1
        if difference == length:
            continue

        # we update the best difference
        if difference > max_difference:
            max_difference = difference
            best_index_set_0 = index_set_0
            best_qubit = qubit

            # this will return 0 if qubit has less 0
            # this will return 1 if qubit has more 0
            best_value = bool(length < (1 << length0))

    assert best_qubit is not None
    assert len(best_index_set_0) != 0 and len(best_index_set_0) != length

    best_index_set = best_index_set_0 if best_value == 0 else indices - best_index_set_0

    return best_index_set, best_qubit, best_value


def cardinality_reduction(circuit: QCircuit, state: QState, verbose_level: int = 0):
    """Select indices for the QState .

    :param state: [description]
    :type state: QState
    """

    diff_qubits = []
    diff_values = []

    # we first select the indices that maximize the difference
    diff_lits = []

    indices = set(list(state.index_set)[:])
    while len(indices) > 1:
        index_set, qubit, value = _maximize_difference_once(state, indices, diff_lits)

        diff_lits.append((qubit, value))

        indices = index_set

    assert len(indices) == 1

    index1 = list(indices)[0]

    if verbose_level >= 3:
        print(f"indices: {indices}, diff_lits: {diff_lits}")

    # we will later use diff_qubit and diff_value as CNOTs
    diff_qubit, diff_value = diff_lits.pop()

    # now we select the second index
    index2_candidates = set()
    for index in set(state.index_set) - indices:
        violated: bool = False
        for _diff_qubit, _diff_value in diff_lits:
            if (index >> _diff_qubit) & 1 != _diff_value:
                violated = True
                break
        if violated:
            continue
        # we add the index to the candidates
        index2_candidates.add(index)

    # we select the second index
    indices = set(list(index2_candidates)[:])
    while len(indices) > 1:
        index_set, qubit, value = _maximize_difference_once(state, indices, diff_lits)
        diff_lits.append((qubit, value))
        indices = index_set

    assert (
        len(indices) == 1
    ), f"indices: {indices}, index2_candidates: {index2_candidates}, diff_lits: {diff_lits}"

    index2 = list(indices)[0]

    if verbose_level >= 3:
        print(f"indices: {indices}, diff_lits: {diff_lits}")
        print(f"merging indices from {index1} to {index2}")

    gates = []

    new_state: QState = state
    for qubit in range(state.num_qubits):
        if (index1 >> qubit) & 1 == (index2 >> qubit) & 1:
            continue

        if qubit == diff_qubit:
            continue

        control_qubit = circuit.qubit_at(diff_qubit)
        control_phase = diff_value
        target_qubit = circuit.qubit_at(qubit)

        gate = CX(control_qubit, control_phase, target_qubit)
        gates.append(gate)
        new_state = gate.apply(new_state)
        if verbose_level >= 3:
            print(f"\t adding gate {gate} to the circuit, new_state: {new_state}")

    diff_qubits, diff_values = [], []
    if len(diff_lits) > 0:
        diff_qubits, diff_values = zip(*diff_lits)

    control_qubits = [circuit.qubit_at(qubit) for qubit in diff_qubits]
    control_phases = diff_values
    target_qubit = circuit.qubit_at(diff_qubit)

    assert index2 in new_state.index_to_weight
    reversed_index2 = index2 ^ (1 << diff_qubit)
    assert reversed_index2 in new_state.index_to_weight
    if verbose_level >= 3:
        print(
            f"index2 = {index2}, reversed_index2: {reversed_index2}, index_to_weight: {new_state.index_to_weight}"
        )

    # we now merge from reversed_index2 to index2

    idx0 = reversed_index2 & ~(1 << diff_qubit)
    idx1 = reversed_index2 | (1 << diff_qubit)

    theta = 2 * np.arctan(
        new_state.index_to_weight[idx1] / new_state.index_to_weight[idx0]
    )

    if (index2 >> diff_qubit) & 1 == 1:
        # from 0 to 1
        theta = theta - np.pi

    gate = MCRY(theta, control_qubits, control_phases, target_qubit)
    gates.append(gate)
    new_state = gate.conjugate().apply(new_state)
    if verbose_level >= 3:
        print(f"\t adding gate {gate} to the circuit, new_state: {new_state}")

    return new_state, gates[::-1]


def sparse_state_synthesis(state: QState, verbose_level: int = 0):
    """This function is used to synthesis sparse state.

    reference: https://github.com/qclib/qclib/blob/master/qclib/state_preparation/merge.py

    """

    circuit = QCircuit(state.num_qubits)

    # deep copy
    curr_state = QState(state.index_to_weight, state.num_qubits)

    gates = []

    while True:
        density = len(curr_state.index_set)
        if verbose_level >= 3:
            print(f"Current state: {curr_state}, density: {density}")
        # we reach the end of the state
        if density == 1:
            break

        curr_state, _gates = cardinality_reduction(
            circuit, curr_state, verbose_level=verbose_level
        )
        for gate in _gates[::-1]:
            gates.append(gate)

    _, _gates = x_reduction(circuit, curr_state, enable_cnot=False)
    circuit.add_gates(_gates + gates[::-1])

    return circuit
