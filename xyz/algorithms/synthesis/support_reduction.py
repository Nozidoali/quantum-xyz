#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-09-10 19:24:34
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-10 22:25:33
'''

import copy

from xyz.circuit.basic_gates.cx import CX
from xyz.circuit.basic_gates.x import X
from xyz.circuit.qcircuit import QCircuit
from xyz.srgraph.operators.qstate.qstate import QState
from xyz.srgraph import XOperator, CXOperator


def support_reduction(circuit: QCircuit, state: QState):
    """Apply the reduction to the circuit .

    :param circuit: [description]
    :type circuit: QCircuit
    :param state: [description]
    :type state: QState
    """
    
    # for collisions
    signature_to_qubits = {}
    
    signatures = state.get_qubit_signatures()
    const1 = state.get_const1_signature()
    
    gates = []
        
    new_state = QState(state.index_to_weight, state.num_qubits)
    
    for qubit_index, signature in enumerate(signatures):
        
        # this is already not a support
        if signature == 0:
            continue
        
        # this is not a support if we use a X gate
        if signature == const1:
            gate = X(circuit.qubit_at(qubit_index))
            gates.append(gate)
            operation = XOperator(qubit_index)
            new_state = operation(new_state)
            continue
        
        # this is not a support if we use a CNOT gate
        if signature in signature_to_qubits:
            control_qubit = circuit.qubit_at(signature_to_qubits[signature])
            target_qubit = circuit.qubit_at(qubit_index)
            control_phase = True
            
            gate = CX(control_qubit, control_phase, target_qubit)
            gates.append(gate)
            operation = CXOperator(qubit_index, signature_to_qubits[signature], target_qubit)
            new_state = operation(new_state)
            continue
            
        # this is not a support if we use a CNOT gate
        if signature ^ const1 in signature_to_qubits:
            control_qubit = circuit.qubit_at(signature_to_qubits[signature ^ const1])
            target_qubit = circuit.qubit_at(qubit_index)
            control_phase = False
            
            gate = CX(control_qubit, control_phase, target_qubit)
            gates.append(gate)
            operation = CXOperator(qubit_index, signature_to_qubits[signature ^ const1], target_qubit)
            new_state = operation(new_state)
            continue
            
        signature_to_qubits[signature] = qubit_index
        
    return new_state, gates