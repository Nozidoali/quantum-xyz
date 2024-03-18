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

    # we first add a rotation_entry gate to the pivot qubit
    theta = 2 * np.arctan(weights1 / weights0)
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


MIN_ROTATION_ANGLE_SEPARATION = 1e0


def _rotation_angles_optimization(
    rotation_angles: List[float], control_indices: List[int]
):
    assert len(rotation_angles) == 1 << len(
        control_indices
    ), f"len(rotation_angles) = {len(rotation_angles)}, len(control_indices) = {len(control_indices)}"

    dont_cares = set()

    # get all the don't cares
    for index in range(len(control_indices)):
        # check if it is a don't care
        index_is_dont_care = True
        for rotation_index, rotation_angle in enumerate(rotation_angles):
            reversed_index = rotation_index ^ (1 << index)
            if not np.isclose(
                rotation_angles[reversed_index],
                rotation_angle,
                atol=MIN_ROTATION_ANGLE_SEPARATION,
            ):
                index_is_dont_care = False
                break
        if index_is_dont_care:
            dont_cares.add(index)

    if len(dont_cares) == 0:
        # no optimization is needed
        return rotation_angles, control_indices

    # now we reindex the rotation_entry angles
    # print(f"rotation_angles = {rotation_angles}")
    # print(f"reduced {len(dont_cares)} don't cares, dont_cares = {dont_cares}")

    # prepare the new rotation_entry control indices
    new_control_indices = []
    old_indices = []
    for old_index, control_index in enumerate(control_indices):
        if old_index not in dont_cares:
            new_control_indices.append(control_index)
            old_indices.append(old_index)

    # prepare the new rotation_entry angles
    new_rotation_angles = []
    for new_index in range(1 << len(new_control_indices)):
        old_index = 0
        for i in range(len(new_control_indices)):
            old_index |= ((new_index >> i) & 1) << old_indices[i]
        new_rotation_angles.append(rotation_angles[old_index])

    return new_rotation_angles, new_control_indices


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

    # we first prepare the rotation_entry table
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

    for i, rotation_entry in enumerate(rotation_table):
        if rotation_entry[0] == 0:
            rotation_angles[i] = np.pi
        elif rotation_entry[1] == 0:
            rotation_angles[i] = 0
        else:
            rotation_angles[i] = 2 * np.arctan(rotation_entry[1] / rotation_entry[0])

    rotation_angles, control_indices = _rotation_angles_optimization(
        rotation_angles, control_indices
    )

    if len(rotation_angles) == 1:
        ry_gate = RY(rotation_angles[0], circuit.qubit_at(pivot))
        gates = [ry_gate]

    else:
        gate = MCMY(
            rotation_angles,
            [circuit.qubit_at(support) for support in control_indices],
            circuit.qubit_at(pivot),
        )
        gates = [gate]

    # we update the state
    index_to_weight = {index: 0 for index in state.index_set}
    for index, weight in state.index_to_weight.items():
        idx0 = index & ~(1 << pivot)
        idx1 = index | (1 << pivot)
        reversed_idx = index ^ (1 << pivot)
        if reversed_idx not in state.index_to_weight:
            index_to_weight[idx0] = weight
            continue
        weight0 = state.index_to_weight[idx0]
        weight1 = state.index_to_weight[idx1]
        index_to_weight[idx0] = np.sqrt(weight0 ** 2 + weight1 ** 2)

    new_state = QState(index_to_weight, state.num_qubits)

    return gates, new_state
