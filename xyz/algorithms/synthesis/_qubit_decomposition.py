#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:48:05
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 13:05:14
"""

import threading
import random
import numpy as np

from typing import List

from xyz.circuit import QGate, QGateType, QBit, CX, CRY
from xyz.circuit.basic_gates.mcry import MCRY
from xyz.circuit.basic_gates.ry import RY

from xyz.circuit.qcircuit import QCircuit
from xyz.qstate import QState
from ._exact_cnot_synthesis import exact_cnot_synthesis


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


def _qubit_decomposition_impl(
    circuit: QCircuit,
    gates: List[QGate],
    state: QState,
    optimality_level: int = 3,
    multi_thread: bool = False,
    verbose_level: int = 0,
    runtime_limit: int = None,
):
    assert len(gates) == 0

    supports = state.get_supports()
    num_supports = len(supports)

    if num_supports <= 4:
        # we can use optimality_level=3
        exact_gates = exact_cnot_synthesis(
            circuit,
            state,
            optimality_level=3,
            verbose_level=verbose_level,
            runtime_limit=runtime_limit,
        )
        for gate in exact_gates:
            gates.append(gate)
        return

    complexity_estimation = (1 << num_supports) * state.get_sparsity()
    OPTIZATION_COMPLEXITY2 = 1 << 8
    OPTIZATION_COMPLEXITY1 = 1 << 10
    if complexity_estimation <= OPTIZATION_COMPLEXITY2:
        # we can use optimality_level=2
        exact_gates = exact_cnot_synthesis(
            circuit,
            state,
            optimality_level=2,
            verbose_level=verbose_level,
            runtime_limit=runtime_limit,
        )
        for gate in exact_gates:
            gates.append(gate)
        return

    if complexity_estimation <= OPTIZATION_COMPLEXITY1:
        # we can use optimality_level=1
        exact_gates = exact_cnot_synthesis(
            circuit,
            state,
            optimality_level=1,
            verbose_level=verbose_level,
            runtime_limit=runtime_limit,
        )
        for gate in exact_gates:
            gates.append(gate)
        return

    # randomly choose a qubit to split
    pivot = random.choice(supports)
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
                runtime_limit,
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
                runtime_limit,
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
            runtime_limit,
        )
        _qubit_decomposition_impl(
            circuit,
            neg_gates,
            neg_state,
            optimality_level,
            multi_thread,
            verbose_level,
            runtime_limit,
        )

    for gate in pos_gates:
        controlled_gate = to_controlled_gate(gate, pivot_qubit, True)
        gates.append(controlled_gate)

    for gate in neg_gates:
        controlled_gate = to_controlled_gate(gate, pivot_qubit, False)
        gates.append(controlled_gate)


def qubit_decomposition(
    circuit: QCircuit,
    target_state: QState,
    optimality_level: int,
    verbose_level: int,
    runtime_limit: int = None,
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
        runtime_limit=runtime_limit,
    )

    return gates
