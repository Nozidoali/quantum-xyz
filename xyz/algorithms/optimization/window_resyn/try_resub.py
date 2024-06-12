#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-25 19:32:29
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-27 04:59:32
"""

import numpy as np

from .lstsq_solver import LstSqSolver

def try_resub(ry_angles_begin: dict, ry_angles_end: dict, cnot_configuration: list, phases: list = True):
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
