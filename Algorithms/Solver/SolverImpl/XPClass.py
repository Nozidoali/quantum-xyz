#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-25 13:35:16
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 14:49:02
'''

from .Detail import *

from typing import List, Tuple

def lt(state1: List[int], state2: List[int]):

    sorted_state1 = sorted(list(state1))
    sorted_state2 = sorted(list(state2))
    
    for i in range(len(state2)):
        if i >= len(state1):
            return True
        if sorted_state1[i] < sorted_state2[i]:
            return True
        elif sorted_state1[i] > sorted_state2[i]:
            return False
    
    return False

def X_equivalence(state: List[int], num_qubits: int) -> List[CnRyMove]:

    # Pauli-X equivalence
    #  note that the following properties hold:
    #  1. X^2 = I
    #  2. X^T = X
    # which means that X is a unitary matrix, and also a Hermitian matrix

    transitions = []
    curr_state = list(state)[:]
    for pivot_qubit in range(num_qubits):
        rotated_state = __apply_X__(curr_state, pivot_qubit)
        if lt(rotated_state, curr_state):
            curr_state = rotated_state[:]
            transitions.append((curr_state, CnRyMove(pivot_qubit, None, 0, [], CnRYDirection.SWAP)))   
    return curr_state, transitions

def __apply_X__(states: List[int], pivot_qubit: int) -> List[int]:
    new_states = []
    for state in states:
        new_states.append(state ^ (1 << pivot_qubit))
    return new_states

def to_canonical_state(state: List[int], num_qubits: int) -> Tuple[CnRyCanonicalState, List[CnRyMove]]:
    
    return X_equivalence(state, num_qubits)