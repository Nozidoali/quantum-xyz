#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-17 22:24:18
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 02:25:07
"""


from xyz.circuit import QCircuit

from .window_resyn import extract_windows_naive, extract_windows, resynthesize_window


def resynthesis(
    circuit: QCircuit, use_advanced_windowing: bool = True, verbose_level: int = 0
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
    new_circuit = QCircuit(circuit.get_num_qubits())

    for target_qubit, window, state_begin, state_end in windows:
        new_window = resynthesize_window(target_qubit, window, state_begin, state_end)
        new_circuit.add_gates(new_window)

        if verbose_level >= 1:
            n_cnots_old = sum((g.get_cnot_cost() for g in window))
            n_cnots_new = sum((g.get_cnot_cost() for g in new_window))
            print(f"n_cnots_old: {n_cnots_old}, n_cnots_new: {n_cnots_new}")

    return new_circuit
