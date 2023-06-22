#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 17:22:44
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 17:23:07
'''

from .CnRyState import *


def move_to_neighbour(curr_state: CnRyState, num_controls: int, pivot_qubit: int, control_state: int, direction: int) -> CnRyState:

    new_states = set()

    for state in curr_state.states:
        # check the unateness
        if (control_state >> state) & 1 == 0:
            new_states.add(state)
            continue
        
        # get the neg state
        neg_state = state & (~(1 << pivot_qubit))
        pos_state = state | (1 << pivot_qubit)

        # we handle the case where both pos_state and neg_state are in the curr_state

        if state == neg_state and pos_state in curr_state.states:
            continue
        
        
        # zero to one, one to zero
        if direction == 1:
            if neg_state in curr_state.states and pos_state not in curr_state.states:
                new_states.add(pos_state)
            elif pos_state in curr_state.states and neg_state not in curr_state.states:
                new_states.add(neg_state)
            elif pos_state in curr_state.states and neg_state in curr_state.states:
                new_states.add(pos_state)
                new_states.add(neg_state)
            else:
                assert False
            continue
        
        # both
        else:
            new_states.add(pos_state)
            new_states.add(neg_state)
            continue
    
    return CnRyState(list(new_states), curr_state.cost + num_controls)