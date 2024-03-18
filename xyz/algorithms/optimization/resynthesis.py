#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-17 22:24:18
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 02:25:07
"""

from xyz.circuit import QCircuit, QBit
from xyz.qstate import QState


def resynthesis_window(
    circuit: QCircuit,
    state_begin: QState,
    state_end: QState,
    target_qubit: QBit,
    n_cnots_max: int,
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

    pass


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
                n_cnots_old = sum((g.get_cnot_cost() for g in curr_window))

                if n_cnots_old == 0:
                    # skip the current window
                    new_circuit.add_gates(curr_window)
                else:
                    # resynthesis the current window
                    n_window += 1
                    print(
                        f"window #{n_window}: state_begin: {state_begin}, state_end: {state_end}"
                    )
                    new_gates = resynthesis_window(
                        new_circuit, state_begin, state_end, curr_target_qubit
                    )
                    new_circuit.add_gates(new_gates)
            curr_window = []
            state_begin = state_end
            curr_target_qubit = gate.target_qubit
        curr_window.append(gate)
        state_end = gate.apply(state_end)

    if len(curr_window) > 0:
        new_circuit.add_gates(curr_window)

    return new_circuit
