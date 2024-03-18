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
from xyz.circuit import QCircuit, QBit, RY, CX
from xyz.qstate import QState
from ._lstsq_solver import LstSqSolver


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

    ry_delta = {
        k: ry_angles_end[k] - ry_angles_begin[k] for k in ry_angles_begin.keys()
    }

    # we can run dependency analysis to find the potential control qubits
    all_control_qubits: list = get_candidate_controls(ry_delta, state_begin.num_qubits)
    n_control_qubits: int = len(all_control_qubits)

    def get_rx(k: int, x: int):
        rx_bool = (constraint_keys[x] >> cnot_configuration[k]) & 1
        rx = 1 if rx_bool == 1 else -1
        return rx

    def get_control_qubit_at(k: int):
        return circuit.qubit_at(cnot_configuration[k])

    for n_cnot_new in range(len(all_control_qubits), n_cnots_old):
        solver = LstSqSolver()

        cnot_configuration = []
        # get all the permutations

        # lets consider more complicated cases later
        if n_control_qubits > 1:
            raise NotImplementedError("n_control_qubits > 1 is not supported yet")

        cnot_configuration = [all_control_qubits[0]]

        thetas = []
        for k in range(n_cnot_new + 1):
            thetas.append(solver.add_variable(f"theta_{k}"))

        phi = []
        for k in range(n_cnot_new + 2):
            curr_phi = []
            for x in range(len(ry_delta)):
                curr_phi.append(solver.add_variable(f"phi_{k}^{x}"))
            phi.append(curr_phi)

        n_constraints: int = len(ry_delta)
        constraint_keys: list = list(ry_delta.keys())

        # add the initial constraints
        for x in range(n_constraints):
            # phi_0^x = ry_angles_begin^x
            solver.add_constraint(
                variables=[phi[0][x]],
                coefficients=[1],
                value=ry_angles_begin[constraint_keys[x]],
            )
            # phi_1^x = phi_0^x + theta_0
            solver.add_constraint(
                variables=[phi[1][x], thetas[0], phi[0][x]], coefficients=[1, -1, -1]
            )
            # phi_n_cnots^x = ry_angles_end^x
            solver.add_constraint(
                variables=[phi[n_cnot_new + 1][x]],
                coefficients=[1],
                value=ry_angles_end[constraint_keys[x]],
            )

        for k in range(n_cnot_new):
            # phi_k+1^x = pi/2 + R_k^x ( phi_k^x - pi/2 ) + theta_k
            for x in range(n_constraints):
                rx = get_rx(k, x)
                solver.add_constraint(
                    variables=[phi[k + 2][x], thetas[k + 1], phi[k + 1][x]],
                    coefficients=[-1, 1, rx],
                    value=np.pi / 2 * (rx - 1),
                )

        solver.solve()
        theta = solver.get_solution(thetas[0])
        new_window = [RY(theta, target_qubit)]
        for k in range(n_cnot_new):
            theta = solver.get_solution(thetas[k + 1])
            new_window += [CX(get_control_qubit_at(k), False, target_qubit)]
            new_window += [RY(theta, target_qubit)]
        # return window_old
        return new_window

    return window_old


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
        new_circuit.add_gates(new_gates)

    return new_circuit
