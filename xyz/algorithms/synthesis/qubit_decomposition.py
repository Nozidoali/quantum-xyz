#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-01 12:48:05
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-01 13:05:14
"""

from calendar import c
import numpy as np
import random
from xyz.circuit import (
    QGate,
    QGateType,
    QBit,
    CX,
    CRY
)
from xyz.circuit.basic_gates.mcry import MCRY
from xyz.circuit.basic_gates.ry import RY

from xyz.circuit.qcircuit import QCircuit
from xyz.srgraph.operators.qstate.qstate import QState

from .exact_cnot_synthesis import exact_cnot_synthesis

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
                gate.get_theta(),
                control_qubit, 
                control_phase, 
                gate.get_target_qubit())
        case QGateType.CX:
            control_qubits = [control_qubit, gate.get_control_qubit()]
            phases = [control_phase, gate.get_phase()]
            return MCRY(
                np.pi, 
                control_qubits,
                phases,
                gate.get_target_qubit())
        case QGateType.CRY:
            control_qubits = [control_qubit, gate.get_control_qubit()]
            phases = [control_phase, gate.get_phase()]
            return MCRY(
                gate.get_theta(),
                control_qubits,
                phases,
                gate.get_target_qubit())    
        
        case QGateType.MCRY:
            control_qubits = [control_qubit] + gate.get_control_qubits()
            phases = [control_phase] + gate.get_phases()
            return MCRY(
                gate.get_theta(), 
                control_qubits,
                phases,
                gate.get_target_qubit())
            
        case _:
            raise NotImplementedError(
                f"Controlled gate {gate.get_qgate_type()} is not implemented"
            )

def _qubit_decomposition_impl(
    circuit: QCircuit, state: QState, optimality_level: int, verbose_level: int
):
    supports = state.get_supports()
    num_supports = len(supports)

    if num_supports <= 4:
        gates = exact_cnot_synthesis(
            circuit, state, optimality_level, verbose_level
        )
        return gates
    
    # else we divide and conquer
    gates = []
    
    # randomly choose a qubit to split
    pivot = random.choice(supports)
    pivot_qubit = circuit.qubit_at(pivot)
    
    neg_state, pos_state, weights0, weights1 = state.cofactors(pivot)
    
    # we first add a rotation gate to the pivot qubit
    theta = 2 * np.arccos(np.sqrt(weights0 / (weights0 + weights1)))
    gate = RY(theta, pivot_qubit)
    gates.append(gate)
    
    
    # then we recursively decompose the two substates
    pos_gates = _qubit_decomposition_impl(
        circuit, pos_state, optimality_level, verbose_level
    )
    neg_gates = _qubit_decomposition_impl(
        circuit, neg_state, optimality_level, verbose_level
    )
    
    for gate in pos_gates:
        controlled_gate = to_controlled_gate(gate, pivot_qubit, True)
        gates.append(controlled_gate)
    
    for gate in neg_gates:
        controlled_gate = to_controlled_gate(gate, pivot_qubit, False)
        gates.append(controlled_gate)
    
    return gates
    
    
def qubit_decomposition(
    circuit: QCircuit, target_state: QState, optimality_level: int, verbose_level: int
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

    return _qubit_decomposition_impl(
        circuit, target_state, optimality_level, verbose_level
    )