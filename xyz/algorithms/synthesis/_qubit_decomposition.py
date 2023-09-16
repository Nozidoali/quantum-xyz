#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:48:05
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 13:05:14
"""

import threading
from typing import List
import numpy as np

from xyz.circuit import QGate, QGateType, QBit, CX, CRY
from xyz.circuit.basic_gates.mcmy import MCMY
from xyz.circuit.basic_gates.mcry import MCRY
from xyz.circuit.basic_gates.ry import RY
from xyz.circuit.decomposition import decompose_mcry, control_sequence_to_gates

from xyz.circuit.qcircuit import QCircuit
from xyz.qstate import QState
from ._exact_cnot_synthesis import exact_cnot_synthesis
from ._support_reduction import support_reduction


def to_controlled_gate(gate: QGate, control_qubit: QBit, control_phase: bool):
    """Return a controlled gate .

    :param gate: [description]
    :type gate: QGate
    :return: [description]
    :rtype: [type]
    """
    assert control_qubit != gate.get_target_qubit()
    match gate.get_qgate_type():
        case QGateType.X:
            return CX(control_qubit, control_phase, gate.get_target_qubit())
        case QGateType.RY:
            return CRY(
                gate.get_theta(), control_qubit, control_phase, gate.get_target_qubit()
            )
        case QGateType.CX:
            control_qubits = [control_qubit, gate.get_control_qubit()]
            phases = [control_phase, gate.get_phase()]
            return MCRY(np.pi, control_qubits, phases, gate.get_target_qubit())
        case QGateType.CRY:
            control_qubits = [control_qubit, gate.get_control_qubit()]
            phases = [control_phase, gate.get_phase()]
            return MCRY(
                gate.get_theta(), control_qubits, phases, gate.get_target_qubit()
            )

        case QGateType.MCRY:
            control_qubits = [control_qubit] + gate.get_control_qubits()
            phases = [control_phase] + gate.get_phases()
            return MCRY(
                gate.get_theta(), control_qubits, phases, gate.get_target_qubit()
            )

        case _:
            raise NotImplementedError(
                f"Controlled gate {gate.get_qgate_type()} is not implemented"
            )


def select_pivot_qubit(state: QState, supports: set):
    """Selects the pivot of the given state .

    :param state: [description]
    :type state: QState
    :param supports: [description]
    :type supports: set
    :return: [description]
    :rtype: [type]
    """
    max_difference: int = -1
    best_qubit = None

    indices = state.index_set

    assert (
        len(indices) >= 2
    ), f"state = {state}, len(indices) = {len(indices)}, supports = {supports}"
    length = len(indices)

    for qubit in supports:
        # we cannot be better than this
        if max_difference == length - 1:
            break

        index_set_0 = set()

        for index in indices:
            if index & (1 << qubit) == 0:
                index_set_0.add(index)

        length0 = len(index_set_0)
        difference = abs(length - (length0 << 1))

        # we update the best difference
        if difference > max_difference:
            max_difference = difference
            best_qubit = qubit

    assert best_qubit is not None
    return best_qubit


def select_informative_qubit(state: QState, supports: set):
    """Selects the smallest qubit in the given state .

    :param state: [description]
    :type state: QState
    :param supports: [description]
    :type supports: set
    :return: [description]
    :rtype: [type]
    """
    best_qubit = None

    indices = state.index_set

    assert (
        len(indices) >= 2
    ), f"state = {state}, len(indices) = {len(indices)}, supports = {supports}"
    length = len(indices)
    min_difference: int = length + 1

    for qubit in supports:
        index_set_0 = set()

        for index in indices:
            if index & (1 << qubit) == 0:
                index_set_0.add(index)

        length0 = len(index_set_0)
        difference = abs(length - (length0 << 1))

        # we update the best difference
        if difference < min_difference:
            min_difference = difference
            best_qubit = qubit

    assert best_qubit is not None
    return best_qubit


def _qubit_decomposition_impl(
    circuit: QCircuit,
    gates: List[QGate],
    state: QState,
    optimality_level: int = 3,
    multi_thread: bool = False,
    verbose_level: int = 0,
    cnot_limit: int = None,
):
    assert len(gates) == 0

    # we first run qubit reduction
    state, support_gates = support_reduction(circuit, state)

    supports = state.get_supports()
    num_supports = len(supports)

    if num_supports <= 4:
        # we can use optimality_level=3
        exact_gates = exact_cnot_synthesis(
            circuit,
            state,
            optimality_level=3,
            verbose_level=verbose_level,
            cnot_limit=cnot_limit,
        )
        for gate in exact_gates:
            gates.append(gate)

        for gate in support_gates:
            gates.append(gate)
        return

    # we select the qubits that maximize the entropy
    pivot = select_pivot_qubit(state, supports)
    pivot_qubit = circuit.qubit_at(pivot)

    neg_state, pos_state, weights0, weights1 = state.cofactors(pivot)

    # we first add a rotation gate to the pivot qubit
    theta = 2 * np.arccos(np.sqrt(weights0 / (weights0 + weights1)))
    gate = RY(theta, pivot_qubit)
    gates.append(gate)

    # then we recursively decompose the two substates
    pos_gates = []
    neg_gates = []

    # using multi_thread, we can parallelize the decomposition
    if multi_thread:
        thread_pos = threading.Thread(
            target=_qubit_decomposition_impl,
            args=(
                circuit,
                pos_gates,
                pos_state,
                optimality_level,
                multi_thread,
                verbose_level,
                cnot_limit,
            ),
        )
        thread_neg = threading.Thread(
            target=_qubit_decomposition_impl,
            args=(
                circuit,
                neg_gates,
                neg_state,
                optimality_level,
                multi_thread,
                verbose_level,
                cnot_limit,
            ),
        )

        thread_pos.start()
        thread_neg.start()

        thread_pos.join()
        thread_neg.join()

    else:
        _qubit_decomposition_impl(
            circuit,
            pos_gates,
            pos_state,
            optimality_level,
            multi_thread,
            verbose_level,
            cnot_limit,
        )
        _qubit_decomposition_impl(
            circuit,
            neg_gates,
            neg_state,
            optimality_level,
            multi_thread,
            verbose_level,
            cnot_limit,
        )

    for gate in pos_gates:
        controlled_gate = to_controlled_gate(gate, pivot_qubit, True)
        gates.append(controlled_gate)

    for gate in neg_gates:
        controlled_gate = to_controlled_gate(gate, pivot_qubit, False)
        gates.append(controlled_gate)

    for gate in support_gates:
        gates.append(gate)


def qubit_decomposition(
    circuit: QCircuit,
    target_state: QState,
    optimality_level: int,
    verbose_level: int,
    cnot_limit: int = None,
):
    """Decompose a circuit into a sequence of single qubit gates and CNOT gates .

    :param circuit: [description]
    :type circuit: QCircuit
    :param state: [description]
    :type state: QState
    :param optimality_level: [description]
    :type optimality_level: int
    :return: [description]
    :rtype: [type]
    """

    gates = []

    _qubit_decomposition_impl(
        circuit,
        gates,
        target_state,
        optimality_level,
        True,
        verbose_level,
        cnot_limit=cnot_limit,
    )

    return gates


def qubit_decomposition_opt(
    circuit: QCircuit,
    state: QState,
    supports: set,
):
    """Composes a circuit decomposition for a circuit .

    the main difference is that, in this implementation:
        1. we do not synthesize the truth table

    to further improve, maybe we can check the actual supports

    :param circuit: [description]
    :type circuit: QCircuit
    :param state: [description]
    :type state: QState
    :param supports: [description]
    :type supports: set
    :return: [description]
    :rtype: [type]
    """
    # we randomly select a pivot qubit
    pivot = select_informative_qubit(state, supports)

    # we first prepare the rotation table
    # the pivot is the target qubit,
    # and the other qubits are the control qubits
    control_indices = list(set(supports) - {pivot})

    rotation_table = [[0, 0] for _ in range(1 << len(control_indices))]

    for index, weight in state.index_to_weight.items():
        rotation_index: int = 0
        for i, support in enumerate(control_indices):
            if index & (1 << support) != 0:
                rotation_index |= 1 << i

        if index & (1 << pivot) != 0:
            rotation_table[rotation_index][1] = weight
        else:
            rotation_table[rotation_index][0] = weight

    rotation_angles = [0 for _ in range(1 << len(control_indices))]

    for i, rotation in enumerate(rotation_table):
        if rotation[0] == 0:
            rotation_angles[i] = np.pi
        elif rotation[1] == 0:
            rotation_angles[i] = 0
        else:
            rotation_angles[i] = 2 * np.arccos(
                np.sqrt(rotation[0] / (rotation[0] + rotation[1]))
            )

    if len(rotation_angles) == 1:
        ry_gate = RY(rotation_angles[0], circuit.qubit_at(pivot))
        gates = [ry_gate]

    else:
        
        gate = MCMY(rotation_angles, [circuit.qubit_at(support) for support in control_indices], circuit.qubit_at(pivot))
        
        gates = [gate]
        


    # we update the state
    index_to_weight = {index: 0 for index in state.index_set}
    for index, weight in state.index_to_weight.items():
        if index & (1 << pivot) == 0:
            index_to_weight[index] += weight
        else:
            index_to_weight[index ^ (1 << pivot)] = weight + state.index_to_weight.get(
                index ^ (1 << pivot), 0
            )

    new_state = QState(index_to_weight, state.num_qubits)

    return gates, new_state
