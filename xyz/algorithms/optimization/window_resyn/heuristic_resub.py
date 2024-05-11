#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-25 20:21:01
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-03 23:15:39
"""

from xyz.circuit import QBit, RY, CX
from xyz.circuit import QState, is_equal
from xyz.algorithms.prepare_state.rotation_angles import get_rotation_table
from .try_resub import try_resub


def resub0(
    target_qubit: QBit,
    window_old: list,
    state_begin: QState,
    state_end: QState,
    verbose_level: int = 0,
):
    assert target_qubit.index != None
    assert state_begin.num_qubits == state_end.num_qubits
    assert verbose_level >= 0

    n_cnots_old = sum((g.get_cnot_cost() for g in window_old))

    if n_cnots_old == 0:
        # skip the resynthesis
        return window_old

    # we try resubstitution
    states = [state_begin]
    state = state_begin
    for gate in window_old:
        state = gate.apply(state)
        states.append(state)

    gate_taken = [True for _ in window_old]
    for i in range(len(states)):
        if not gate_taken[i - 1]:
            continue
        for j in range(len(states) - 1, i, -1):
            if is_equal(states[i], states[j]):
                # we remove the gates between i and j
                for k in range(i + 1, j):
                    gate_taken[k] = False
                break

    new_window = [g for i, g in enumerate(window_old) if gate_taken[i]]

    return new_window


def resub1(
    target_qubit: QBit,
    window_old: list,
    state_begin: QState,
    state_end: QState,
    verbose_level: int = 0,
):
    assert target_qubit.index != None
    assert verbose_level >= 0

    n_cnots_old = sum((g.get_cnot_cost() for g in window_old))

    if n_cnots_old <= 1:
        # skip the resynthesis
        return window_old

    ry_angles_begin: dict = get_rotation_table(state_begin, target_qubit.index)
    ry_angles_end: dict = get_rotation_table(state_end, target_qubit.index)

    # we can run dependency analysis to find the potential control qubits
    # all_control_qubits: list = get_candidate_controls(ry_delta, state_begin.num_qubits)
    # n_control_qubits: int = len(all_control_qubits)

    all_control_qubits = set()
    for gate in window_old:
        if isinstance(gate, CX):
            all_control_qubits.add(gate.control_qubit.index)
    all_control_qubits = list(all_control_qubits)

    n_cnot_new = 1
    for control_qubit in all_control_qubits:
        # for control_qubit in range(state_begin.num_qubits):
        #     if control_qubit == target_qubit.index:
        #         continue
        cnot_configuration = [control_qubit]
        success, thetas = try_resub(ry_angles_begin, ry_angles_end, cnot_configuration)
        if success:
            new_window = [RY(thetas[0], target_qubit)]
            for k in range(n_cnot_new):
                new_window += [CX(QBit(cnot_configuration[k]), False, target_qubit)]
                new_window += [RY(thetas[k + 1], target_qubit)]
            return new_window

    return window_old


def resubN(
    target_qubit: QBit,
    window_old: list,
    state_begin: QState,
    state_end: QState,
    verbose_level: int = 0,
):
    assert verbose_level >= 0

    all_control_qubits = set()
    for gate in window_old:
        if isinstance(gate, CX):
            all_control_qubits.add(gate.control_qubit.index)
    all_control_qubits = list(all_control_qubits)
    n_cnot_new = len(all_control_qubits)

    n_cnots_old = sum((g.get_cnot_cost() for g in window_old))

    if n_cnots_old <= n_cnot_new:
        # skip the resynthesis
        return window_old

    ry_angles_begin: dict = get_rotation_table(state_begin, target_qubit.index)
    ry_angles_end: dict = get_rotation_table(state_end, target_qubit.index)

    # we can run dependency analysis to find the potential control qubits
    # all_control_qubits: list = get_candidate_controls(ry_delta, state_begin.num_qubits)
    # n_control_qubits: int = len(all_control_qubits)

    cnot_configuration = all_control_qubits

    def get_control_qubit_at(k: int):
        return QBit(cnot_configuration[k])

    new_window = None
    success, thetas = try_resub(ry_angles_begin, ry_angles_end, cnot_configuration)
    if not success:
        # we cannot find a solution
        new_window = window_old[:]
    else:
        new_window = [RY(thetas[0], target_qubit)]
        for k in range(n_cnot_new):
            new_window += [CX(get_control_qubit_at(k), False, target_qubit)]
            new_window += [RY(thetas[k + 1], target_qubit)]

    return new_window


def resub2N(
    target_qubit: QBit,
    window_old: list,
    state_begin: QState,
    state_end: QState,
    verbose_level: int = 0,
):
    assert verbose_level >= 0

    all_control_qubits = set()
    for gate in window_old:
        if isinstance(gate, CX):
            all_control_qubits.add(gate.control_qubit.index)
    all_control_qubits = list(all_control_qubits)
    n_cnot_new = 2 * len(all_control_qubits) + 1

    n_cnots_old = sum((g.get_cnot_cost() for g in window_old))

    if n_cnots_old <= n_cnot_new:
        # skip the resynthesis
        return window_old

    ry_angles_begin: dict = get_rotation_table(state_begin, target_qubit.index)
    ry_angles_end: dict = get_rotation_table(state_end, target_qubit.index)

    # we can run dependency analysis to find the potential control qubits
    # all_control_qubits: list = get_candidate_controls(ry_delta, state_begin.num_qubits)
    # n_control_qubits: int = len(all_control_qubits)

    cnot_configuration = all_control_qubits[:] + all_control_qubits[1::-1]

    def get_control_qubit_at(k: int):
        return QBit(cnot_configuration[k])

    new_window = None
    success, thetas = try_resub(ry_angles_begin, ry_angles_end, cnot_configuration)
    if not success:
        # we cannot find a solution
        new_window = window_old[:]
    else:
        new_window = [RY(thetas[0], target_qubit)]
        for k in range(n_cnot_new):
            new_window += [CX(get_control_qubit_at(k), False, target_qubit)]
            new_window += [RY(thetas[k + 1], target_qubit)]

    return new_window
