#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-09-08 12:59:35
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-08 15:43:09
'''


import random
from xyz.circuit.qcircuit import QCircuit

from xyz.srgraph.operators.qstate.qstate import QState


def merge_index(circuit: QCircuit, state: QState, index_from: int, index_to: int, verbose_level: int = 0):
    """Merge two circuit indices into a single index .
    
    This function reimplements the method proposed in paper:
    An Efficient Algorithm for Sparse Quantum State Preparation
    https://ieeexplore.ieee.org/document/9586240
    
    
    :param circuit: [description]
    :type circuit: QCircuit
    :param index_from: [description]
    :type index_from: str
    :param index_to: [description]
    :type index_to: str
    :param verbose_level: [description], defaults to 0
    :type verbose_level: int, optional
    """
    
    index_diff = index_from ^ index_to
    
    # dif_qubits
    diff_qubits = []
    diff_vals = []
    
    # get the first different bit
    target_qubit: int = None
    for i in range(state.num_qubits):
        if index_diff & (1 << i) != 0:
            target_qubit = i
            break
    
    if verbose_level >= 3:
        print(f"Merging {index_from} to {index_to} by flipping {target_qubit}")
    
    new_index = index_from ^ (1 << target_qubit)
    
    if new_index == index_to:
        # in this case we need a rotation gate
        pass

def sparse_state_synthesis(state: QState, map_gates: bool = False, verbose_level: int = 0):
    """This function is used to synthesis sparse state.
    """
    
    # initialize the circuit
    circuit = QCircuit(state.num_qubits, map_gates=map_gates)
    
    # deep copy
    curr_state = QState(state.index_to_weight, state.num_qubits)
    
    while True:
        density = len(state.index_set)
    
        # we reach the end of the state
        if density == 1:
            break
    
        if verbose_level >= 3:
            for i, index in enumerate(curr_state.index_set):
                index_str = bin(index)[2:].zfill(state.num_qubits)
                print(f"{i}: {index_str}")
        
        # randomly select a index:
        index1 = random.choice(list(curr_state.index_set))
        index1_str = bin(index1)[2:].zfill(state.num_qubits)
        
        # we find the index closest to the target index
        index2: int = None
        best_dist: int = None
        
        index: int
        for index in list(curr_state.index_set):
            
            # skip the same index
            if index == index1:
                continue
            
            # get the number of different bits between index and index2
            index_str = bin(index)[2:].zfill(state.num_qubits)
            dist = sum([1 for i in range(state.num_qubits) if index_str[i] != index1_str[i]])
            
            
            if best_dist is None or dist < best_dist:
                best_dist = dist
                index2 = index
            
        index2_str = bin(index2)[2:].zfill(state.num_qubits)
        
        if verbose_level >= 3:
            print(f"index1: {index1}, index2: {index2}")
            print(f"index1_str: {index1_str}, index2_str: {index2_str}")
            
        # merge the two indices
        merge_index(circuit, curr_state, index1, index2, verbose_level)

        exit(0)
        
    return circuit