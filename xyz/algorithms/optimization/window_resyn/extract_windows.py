#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-04-22 18:35:53
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-22 20:33:20
'''

from xyz.circuit import QCircuit, QBit
from xyz.qstate import QState

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