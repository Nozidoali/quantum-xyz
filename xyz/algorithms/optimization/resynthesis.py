#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-17 22:24:18
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 02:25:07
"""

import numpy as np
from typing import List
from xyz.circuit import QCircuit, QBit
from xyz.qstate import QState

def get_candidate_controls(rotation_table: dict, num_qubits: int) -> List[int]:
    """
    get_candidate_controls:
    return the possible control qubits for the given rotation table:
    
    
    """
    selected = set()
    candidates = list(range(num_qubits))
    for index, theta in rotation_table.items():
        candidates_to_remove: set = set()
        for qubit_index in candidates:
            index_reversed = index ^ (1 << qubit_index)
            if index_reversed not in rotation_table:
                continue
            theta_reversed: float = rotation_table[index_reversed]
            if np.isclose(theta, theta_reversed):
                continue
            selected.add(qubit_index)
            candidates_to_remove.add(qubit_index)
        for qubit_index in candidates_to_remove:
            candidates.remove(qubit_index)
            
    return list(selected)

def resynthesis_window(
    circuit: QCircuit,
    state_begin: QState,
    state_end: QState,
    target_qubit: QBit,
    window_old: list,
):
    """
    resynthesis_window
    return the new gates that can be used to replace the current window

    :param circuit: the circuit to be resynthesized
    :type circuit: QCircuit
    :param state_begin: start state of the window
    :type state_begin: QState
    :param state_end: the end state of the window
    :type state_end: QState
    :param target_qubit: the target qubit of the window
    :type target_qubit: QBit
    :param n_cnots_max: the maximum number of CNOTs allowed in the resynthesized circuit
    :type n_cnots_max: int
    """
    
    n_cnots_old = sum((g.get_cnot_cost() for g in window_old))
    
    if n_cnots_old == 0:
        # skip the resynthesis
        return window_old

    ry_angles_begin: dict = state_begin.get_rotation_table(target_qubit.index)
    ry_angles_end: dict = state_end.get_rotation_table(target_qubit.index)
    
    ry_delta = {k: ry_angles_end[k] - ry_angles_begin[k] for k in ry_angles_begin.keys()}
    
    # we can run dependency analysis to find the potential control qubits
    all_control_qubits: list = get_candidate_controls(ry_delta, state_begin.num_qubits)
    
    if len(all_control_qubits) >= n_cnots_old:
        # no need to resynthesize
        return window_old
    
    print(
        f"state_begin: {state_begin}, state_end: {state_end}, n_cnots = {n_cnots_old}"
    )
    print(f"ry_delta: {ry_delta}, all_control_qubits: {all_control_qubits}")
    
    # get all the permutations
    
    
    # we construct the linear system
    
    return []


def resynthesis(circuit: QCircuit) -> QCircuit:
    """
    Extract windows from the given circuit
    The idea is similar to rip-up and reroute in VLSI design. We extract windows from the circuit and resynthesize each window to minimize the number of CNOTs.

    TODO: maximize the size of each window
    """

    curr_target_qubit: QBit = None
    curr_window: list = []
    n_window: int = 0

    new_circuit = QCircuit(
        num_qubits=circuit.get_num_qubits(), map_gates=circuit.map_gates
    )

    state_begin: QState = QState.ground_state(circuit.get_num_qubits())
    state_end: QState = QState.ground_state(circuit.get_num_qubits())
    for gate in circuit.get_gates():
        if gate.target_qubit != curr_target_qubit:
            if len(curr_window) > 0:
                # resynthesis the current window
                n_window += 1
                new_gates = resynthesis_window(
                    circuit, state_begin, state_end, curr_target_qubit, curr_window
                )
                new_circuit.add_gates(new_gates)
            curr_window = []
            state_begin = state_end
            curr_target_qubit = gate.target_qubit
        curr_window.append(gate)
        state_end = gate.apply(state_end)

    if len(curr_window) > 0:
        n_window += 1
        new_gates = resynthesis_window(
            circuit, state_begin, state_end, curr_target_qubit, curr_window
        )

    return new_circuit
