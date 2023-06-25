#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-25 12:17:22
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 17:05:25
'''

from typing import List
from .CnRyMove import *

def get_all_cnot_moves(num_qubits: int) -> List[CnRyMove]:

    moves = []

    for pivot_qubits in range(num_qubits):
        moves += get_all_moves(num_qubits, pivot_qubits, 1)

    return moves

def get_all_moves(num_qubits: int, pivot_qubit: int, max_controls: int = None) -> List[CnRyMove]:
    '''
    return all the control states that can be used to control the pivot_qubit
    
    Args:
        num_qubits: the number of qubits
        pivot_qubit: the qubit to be controlled

    the pivot qubit cannot be controlled by itself
    '''

    def dfs(num_qubits: int, curr_bit: int, curr_state: int, curr_num_controls: int, curr_control_states: list, moves: List[int]):

        if curr_bit == num_qubits:
            # both directions
            moves.append(CnRyMove(pivot_qubit, curr_state, curr_num_controls, curr_control_states, CnRYDirection.SWAP))
            moves.append(CnRyMove(pivot_qubit, curr_state, curr_num_controls, curr_control_states, CnRYDirection.MERGE))
            return
        
        if curr_bit == pivot_qubit:
            dfs(num_qubits, curr_bit + 1, curr_state, curr_num_controls, curr_control_states, moves)
            return
        
        # we have 3 cases
        # 1. the curr_bit is not controlled
        dfs(num_qubits, curr_bit + 1, curr_state, curr_num_controls, curr_control_states, moves)

        new_state = 0
        for i in range(1<<num_qubits):
            if (i >> curr_bit) & 1 == 0:
                new_state |= (1 << i)

        neg_state = new_state
        pos_state = (~new_state) & ((1 << (1<<num_qubits)) - 1)

        # print("curr_bit: ", curr_bit)
        # print("neg_state: ", bin(neg_state))
        # print("pos_state: ", bin(pos_state))

        nonlocal max_controls        
        
        if max_controls is not None and curr_num_controls >= max_controls:
            return
        
        # 2. the curr_bit is controlled by 0
        next_control_states = curr_control_states[:]
        next_control_states.append((curr_bit, 0))
        dfs(num_qubits, curr_bit + 1, neg_state & curr_state, curr_num_controls+1, next_control_states, moves)

        # 3. the curr_bit is controlled by 1
        next_control_states = curr_control_states[:]
        next_control_states.append((curr_bit, 1))
        dfs(num_qubits, curr_bit + 1, pos_state & curr_state, curr_num_controls+1, next_control_states, moves)

    moves = []
    init_state = (1 << (1<<num_qubits)) - 1 
    dfs(num_qubits, 0, init_state, 0, [], moves)
    return moves
