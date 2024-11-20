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
from xyz.circuit import (
    QCircuit,
    QBit,
    QState,
    RY,
    CX,
    CRY,
    MCRY,
    is_equal,
    get_rotation_table,
)


class LstSqSolverVar:
    def __init__(self, index: int = None) -> None:
        self.index = index


class LstSqSolver:
    def __init__(self) -> None:
        self._variables = {}
        self._n_vars: int = 0
        self._n_constraints: int = 0
        self._solutions = None
        self._A = []
        self._b = []

    def add_variable(self, name: str) -> LstSqSolverVar:
        new_var = LstSqSolverVar(self._n_vars)
        self._n_vars += 1
        self._variables[name] = new_var
        return new_var

    def get_variable(self, name: str) -> LstSqSolverVar:
        return self._variables[name]

    def get_n_variables(self) -> int:
        return self._n_vars

    def get_n_constraints(self) -> int:
        return self._n_constraints

    def add_constraint(
        self, variables: list, coefficients: list, value: float = 0
    ) -> None:
        assert len(variables) == len(coefficients)
        vector = [0] * self._n_vars
        for i, v in enumerate(variables):
            if isinstance(v, LstSqSolverVar):
                vector[v.index] = coefficients[i]
            elif isinstance(v, int):
                vector[v] = coefficients[i]
            elif isinstance(v, str):
                vector[self._variables[v].index] = coefficients[i]
            else:
                raise ValueError("Invalid variable type")
        self._A.append(vector)
        self._b.append(value)
        self._n_constraints += 1

    def solve(self) -> None:
        sol, residuals, _, _ = np.linalg.lstsq(self._A, self._b, rcond=None)
        if residuals.size > 0 and np.allclose(residuals, 0):
            self._solutions = sol
            if not np.allclose(np.dot(self._A, sol), self._b):
                return False
            return True
        elif residuals.size == 0:
            if not np.allclose(np.dot(self._A, sol), self._b):
                # print("residuals.size == 0")
                # print("sol: ", sol)
                # print(f"difference: {np.dot(self._A, sol) - self._b}")
                return False
            self._solutions = sol
            return True
        else:
            # no solution found
            return False

    def get_solutions(self) -> list:
        return self._solutions

    def get_solution(self, var) -> float:
        if isinstance(var, str):
            return self._solutions[self._variables[var].index]
        if isinstance(var, int):
            return self._solutions[var]
        if isinstance(var, LstSqSolverVar):
            return self._solutions[var.index]
        raise ValueError("Invalid variable type")

    def print(self) -> str:
        for i in range(self._n_constraints):
            print(f"{self._A[i]} = {self._b[i]}")


def try_resub(
    ry_angles_begin: dict,
    ry_angles_end: dict,
    cnot_configuration: list,
    phases: list = True,
):
    def get_rx(k: int, x: int):
        rx_bool = (constraint_keys[x] >> cnot_configuration[k]) & 1
        rx = -1 if rx_bool == phases[k] else 1
        return rx

    solver = LstSqSolver()

    n_cnot_new = len(cnot_configuration)

    thetas = []
    for k in range(n_cnot_new + 1):
        thetas.append(solver.add_variable(f"theta_{k}"))

    phi = []
    for k in range(n_cnot_new + 2):
        curr_phi = []
        for x in range(len(ry_angles_begin)):
            curr_phi.append(solver.add_variable(f"phi_{k}^{x}"))
        phi.append(curr_phi)

    n_constraints: int = len(ry_angles_begin)
    constraint_keys: list = list(ry_angles_begin.keys())

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
            rx = get_rx(k, x)
            solver.add_constraint(
                variables=[phi[k + 2][x], thetas[k + 1], phi[k + 1][x]],
                coefficients=[-1, 1, rx],
                value=np.pi / 2 * (rx - 1),
            )

    # solver.print()

    success = solver.solve()
    if not success:
        # we cannot find a solution
        # print("no solution found")
        return False, None

    # print("solutions: ", solver.get_solutions())
    thetas = [solver.get_solution(theta) for theta in thetas]

    return True, thetas


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
            # this condition is buggy!
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


def resubA(
    target_qubit: QBit,
    window_old: list,
    state_begin: QState,
    state_end: QState,
    verbose_level: int = 0,
):
    ry_angles_begin: dict = get_rotation_table(state_begin, target_qubit.index)
    ry_angles_end: dict = get_rotation_table(state_end, target_qubit.index)
    n_cnot_new = 0

    cnot_configuration = []
    success, thetas = try_resub(ry_angles_begin, ry_angles_end, cnot_configuration)

    if verbose_level >= 1:
        print(f"resubA: target_qubit = {target_qubit}")

    if success:
        new_window = [RY(thetas[0], target_qubit)]
        for k in range(n_cnot_new):
            new_window += [CX(QBit(cnot_configuration[k]), True, target_qubit)]
            new_window += [RY(thetas[k + 1], target_qubit)]
        return new_window
    return window_old


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

    if verbose_level >= 1:
        print(f"resub1: target_qubit = {target_qubit}")

    ry_angles_begin: dict = get_rotation_table(state_begin, target_qubit.index)
    ry_angles_end: dict = get_rotation_table(state_end, target_qubit.index)

    all_control_qubits = set()
    for gate in window_old:
        if isinstance(gate, CX):
            all_control_qubits.add(gate.control_qubit.index)
        if isinstance(gate, CRY):
            all_control_qubits.add(gate.control_qubit.index)
        if isinstance(gate, MCRY):
            for control_qubit in gate.control_qubits:
                all_control_qubits.add(control_qubit.index)
    all_control_qubits = list(all_control_qubits)

    n_cnot_new = 1
    for control_qubit in all_control_qubits:
        for control_phase in [[True], [False]]:
            if verbose_level >= 1:
                print(f"resub1: control_qubit = {control_qubit}")
            # for control_qubit in range(state_begin.num_qubits):
            #     if control_qubit == target_qubit.index:
            #         continue
            cnot_configuration = [control_qubit]
            success, thetas = try_resub(
                ry_angles_begin, ry_angles_end, cnot_configuration, phases=control_phase
            )
            if success:
                new_window = [RY(thetas[0], target_qubit)]
                for k in range(n_cnot_new):
                    new_window += [
                        CX(QBit(cnot_configuration[k]), control_phase[0], target_qubit)
                    ]
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
        if isinstance(gate, CRY):
            all_control_qubits.add(gate.control_qubit.index)
        if isinstance(gate, MCRY):
            for control_qubit in gate.control_qubits:
                all_control_qubits.add(control_qubit.index)
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

    control_phases = [
        # seq for seq in product((True, False), repeat=len(cnot_configuration))
        [False]
        * len(cnot_configuration)
    ]
    for control_phase in control_phases:
        success, thetas = try_resub(
            ry_angles_begin, ry_angles_end, cnot_configuration, control_phase
        )
        if success:
            new_window = [RY(thetas[0], target_qubit)]
            for k in range(n_cnot_new):
                new_window += [
                    CX(get_control_qubit_at(k), control_phase[k], target_qubit)
                ]
                new_window += [RY(thetas[k + 1], target_qubit)]
            return new_window

    return window_old


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

    control_phases = [
        seq for seq in product((True, False), repeat=len(cnot_configuration))
    ]
    for control_phase in control_phases:
        print(control_phase)
        success, thetas = try_resub(
            ry_angles_begin, ry_angles_end, cnot_configuration, control_phase
        )
        if success:
            new_window = [RY(thetas[0], target_qubit)]
            for k in range(n_cnot_new):
                new_window += [
                    CX(get_control_qubit_at(k), control_phase[k], target_qubit)
                ]
                new_window += [RY(thetas[k + 1], target_qubit)]
            return new_window

    return window_old


def resynthesize_window(
    target_qubit: QBit,
    window_old: list,
    state_begin: QState,
    state_end: QState,
    verbose_level: int = 0,
):
    """
    resynthesize_window
    return the new gates that can be used to replace the current window

    :param state_begin: start state of the window
    :type state_begin: QState
    :param state_end: the end state of the window
    :type state_end: QState
    :param target_qubit: the target qubit of the window
    :type target_qubit: QBit
    :param n_cnots_max: the maximum number of CNOTs allowed in the resynthesized circuit
    :type n_cnots_max: int
    """

    if verbose_level >= 1:
        ry_angles_begin: dict = get_rotation_table(state_begin, target_qubit.index)
        ry_angles_end: dict = get_rotation_table(state_end, target_qubit.index)

        ry_delta = {
            k: ry_angles_end[k] - ry_angles_begin[k] for k in ry_angles_begin.keys()
        }
        # print the target
        print("-" * 80)
        print(f"target qubit: {target_qubit}")
        for gate in window_old:
            print(f"\t{gate}")
        print(f"state_begin: {state_begin}")
        print(f"state_end: {state_end}")
        for k in ry_delta.keys():
            print(
                f"\t|{k:0{state_begin.num_qubits}b}>: {ry_angles_begin[k]:0.02f} -> {ry_angles_end[k]:0.02f}"
            )

    new_window = window_old[:]

    new_window = resubA(
        target_qubit=target_qubit,
        window_old=new_window,
        state_begin=state_begin,
        state_end=state_end,
        verbose_level=verbose_level,
    )

    new_window = resub1(
        target_qubit=target_qubit,
        window_old=new_window,
        state_begin=state_begin,
        state_end=state_end,
        verbose_level=verbose_level,
    )

    new_window = resubN(
        target_qubit=target_qubit,
        window_old=new_window,
        state_begin=state_begin,
        state_end=state_end,
        verbose_level=verbose_level,
    )

    # new_window = resub2N(
    #     target_qubit=target_qubit,
    #     window_old=new_window,
    #     state_begin=state_begin,
    #     state_end=state_end,
    #     verbose_level=verbose_level,
    # )

    if verbose_level >= 1:
        print("new window:")
        for gate in new_window:
            print(f"\t{gate}")
        print("-" * 80)

    # check the correctness of the new window
    state: QState = state_begin
    for gate in new_window:
        state = gate.apply(state)
    if not state == state_end:
        raise ValueError("resynthesis failed")

    return new_window


def extract_windows_naive(circuit: QCircuit):
    gates = circuit.get_gates()
    is_taken = [False] * len(gates)

    curr_target_qubit: QBit = None
    curr_window: list = []

    windows = []

    state_begin: QState = QState.ground_state(circuit.get_num_qubits())
    state_end: QState = QState.ground_state(circuit.get_num_qubits())

    for i in range(len(gates)):
        if is_taken[i]:
            continue
        gate = gates[i]
        if gate.target_qubit != curr_target_qubit:
            if len(curr_window) > 0:
                windows.append((curr_target_qubit, curr_window, state_begin, state_end))
            curr_window = []
            curr_target_qubit = gate.target_qubit
            state_begin = state_end
        curr_window.append(gate)
        state_end = gate.apply(state_end)

    if len(curr_window) > 0:
        windows.append((curr_target_qubit, curr_window, state_begin, state_end))

    return windows


def extract_windows(circuit: QCircuit):
    gates = circuit.get_gates()
    is_taken = [False] * len(gates)

    curr_target_qubit: QBit = None
    curr_window: list = []

    windows = []

    state_begin: QState = QState.ground_state(circuit.get_num_qubits())
    state_end: QState = QState.ground_state(circuit.get_num_qubits())

    for i in range(len(gates)):
        if is_taken[i]:
            continue
        gate = gates[i]
        if gate.target_qubit != curr_target_qubit:
            if len(curr_window) > 0:
                uncommute_qubits = set()
                for j in range(i, len(gates)):
                    try:
                        if gates[j].control_qubit == curr_target_qubit:
                            break
                    except AttributeError:
                        pass

                    if gates[j].target_qubit != curr_target_qubit:
                        uncommute_qubits.add(gates[j].target_qubit)
                    else:
                        try:
                            if gates[j].control_qubit in uncommute_qubits:
                                break
                        except AttributeError:
                            pass

                        is_taken[j] = True
                        curr_window.append(gates[j])
                        state_end = gates[j].apply(state_end)

                windows.append((curr_target_qubit, curr_window, state_begin, state_end))
            curr_window = []
            curr_target_qubit = gate.target_qubit
            state_begin = state_end
        curr_window.append(gate)
        state_end = gate.apply(state_end)

    if len(curr_window) > 0:
        windows.append((curr_target_qubit, curr_window, state_begin, state_end))

    return windows


def resynthesis(
    circuit: QCircuit, use_advanced_windowing: bool = False, verbose_level: int = 0
) -> QCircuit:
    """
    Extract windows from the given circuit
    The idea is similar to rip-up and reroute in VLSI design. We extract windows from the circuit and resynthesize each window to minimize the number of CNOTs.

    TODO: maximize the size of each window
    """

    if use_advanced_windowing:
        windows = extract_windows(circuit)
    else:
        windows = extract_windows_naive(circuit)
    new_circuit = QCircuit(circuit.get_num_qubits(), map_gates=circuit.map_gates)

    for target_qubit, window, state_begin, state_end in windows:
        new_window = resynthesize_window(
            target_qubit, window, state_begin, state_end, verbose_level=verbose_level
        )
        new_circuit.add_gates(new_window)

    return new_circuit
