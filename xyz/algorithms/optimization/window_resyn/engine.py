#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-22 18:27:12
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-05 19:13:10
"""

from xyz.circuit import QBit
from xyz.circuit import QState
from .heuristic_resub import resub1, resubN, resubA, resub2N
from xyz.algorithms.prepare_state import get_rotation_table


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

    new_window = resub2N(
        target_qubit=target_qubit,
        window_old=new_window,
        state_begin=state_begin,
        state_end=state_end,
        verbose_level=verbose_level,
    )

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
