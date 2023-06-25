#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-21 14:02:46
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 11:24:56
'''

import numpy as np
from queue import PriorityQueue

from typing import List

from Circuit import *

from Algorithms.Decompose import *
from .Detail import *

from Visualization import *


def get_all_control_states(num_qubits: int, pivot_qubit: int, max_controls: int = None) -> List[int]:
    '''
    return all the control states that can be used to control the pivot_qubit
    
    Args:
        num_qubits: the number of qubits
        pivot_qubit: the qubit to be controlled

    the pivot qubit cannot be controlled by itself
    '''

    def dfs(num_qubits: int, curr_bit: int, curr_state: int, curr_num_controls: int, curr_control_states: list, control_states: List[int]):

        if curr_bit == num_qubits:
            control_states.append((curr_state, curr_num_controls, curr_control_states))
            return
        
        if curr_bit == pivot_qubit:
            dfs(num_qubits, curr_bit + 1, curr_state, curr_num_controls, curr_control_states, control_states)
            return
        
        # we have 3 cases
        # 1. the curr_bit is not controlled
        dfs(num_qubits, curr_bit + 1, curr_state, curr_num_controls, curr_control_states, control_states)

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
        dfs(num_qubits, curr_bit + 1, neg_state & curr_state, curr_num_controls+1, next_control_states, control_states)

        # 3. the curr_bit is controlled by 1
        next_control_states = curr_control_states[:]
        next_control_states.append((curr_bit, 1))
        dfs(num_qubits, curr_bit + 1, pos_state & curr_state, curr_num_controls+1, next_control_states, control_states)

    control_states = []
    init_state = (1 << (1<<num_qubits)) - 1 
    dfs(num_qubits, 0, init_state, 0, [], control_states)
    return control_states

def cnry_solver(final_state: np.ndarray):
    
    init_state = CnRyState()
    num_qubits = int(np.log2(len(final_state)))
    
    visited = set()
    enqueued = {}
    prev = {}
    
    q = PriorityQueue()

    enqueued[init_state] = init_state.cost
    prev[init_state] = None
    q.put(init_state)

    prev_cost = 0

    final_state_ones = np.count_nonzero(final_state)

    while not q.empty():
        
        curr_state = q.get()
        visited.add(curr_state)

        if False:
            curr_state_cost = curr_state.cost
            print(f"curr_state: {curr_state.states}, cost: {curr_state_cost}, qsize: {q.qsize()}")            

        if curr_state == to_cnry_state(final_state):
            print("Solution found, cost = ", curr_state.cost)

            solution = []
            solution.append((curr_state, None))
            prev_state = curr_state
            while True:
                if prev[prev_state] is None:
                    break
                prev_state, qubit, control, control_states, direction = prev[prev_state]

                if True:
                    state_str = [f"{i:b}" for i in prev_state.states]
                    print(f"state: {state_str}, qubit: {qubit}, control: {control:b}, direction: {direction}")
                solution.append((prev_state, (qubit, control, control_states, direction)))
            return solution

        for qubit in range(num_qubits):
            
            states = get_all_control_states(num_qubits, qubit, 1)

            for control, num_controls, control_states in states:
                for direction in [1, 2]:

                    def cost_function(num_controls: int):
                        if num_controls == 0:
                            return 0
                        if direction == 1 and num_controls == 1:
                            return 1
                        return 1 << num_controls
                
                    new_state = move_to_neighbour(curr_state, cost_function(num_controls), qubit, control, direction)

                    # this only works for the non-split
                    if len(new_state.states) > final_state_ones:
                        continue
                    
                    if new_state in visited:
                        continue
                    
                    if new_state in enqueued:
                        if new_state.cost >= enqueued[new_state]:
                            continue

                    enqueued[new_state] = new_state.cost
                    prev[new_state] = curr_state, qubit, control, control_states, direction
                    q.put(new_state)

    # we should not reach here
    print("Error: no solution found")
    
    return None

def solution_to_circuit(num_qubits: int, solution: list) -> QCircuit:

    circuit = QCircuit(num_qubits)
    circuit.set_mapping(True)

    weights = np.zeros(1 << num_qubits)

    mcry_gates = []

    idx: int = 0

    for step in solution:

        states: CnRyState
        states, op = step

        # save the figure
        print_cube(states.states, f"step_{idx}.pdf")
        idx += 1
        
        if op is None:

            # this is the initial state
            # we initialize the weights
            for state in states.states:
                weights[state] = 1
            continue
        
        qubit, control, control_states, direction = op

        thetas: dict = {}

        # we adjust the weights according to the operation        
        for i in range(1<<num_qubits):

            # this bit is not mapped in this iteration
            if (control >> i) & 1 == 0:
                continue

            if (i >> qubit) & 1 == 1:
                continue

            # then we check the direction
            neg_index = i
            pos_index = i ^ (1 << qubit)
            
            if weights[neg_index] == 0 and weights[pos_index] == 0:
                continue
            
            
            if direction == 1:

                # we need to figure out which bit is the src and which bit is the dst
                if weights[neg_index] == 0:
                    src_index = pos_index
                    dst_index = neg_index
                else:
                    src_index = neg_index
                    dst_index = pos_index

                # we need to flip the bit (from the src to dst)
                assert weights[dst_index] == 0
                weights[dst_index] += weights[src_index]
                weights[src_index] = 0

            if direction == 2:

                # we need to merge the weights (from the src to dst)

                if neg_index in states.states:
                    src_index = pos_index
                    dst_index = neg_index
                else:
                    src_index = neg_index
                    dst_index = pos_index
                
                curr_theta = None
                try:
                    print(f"src weight = {weights[src_index]}, dst weight = {weights[dst_index]}")
                    
                    curr_theta = 2 * np.arccos(np.sqrt(weights[dst_index] / (weights[src_index] + weights[dst_index])))

                except:
                    pass
                
                if curr_theta:
                    thetas[curr_theta] = dst_index
                    
                weights[dst_index] += weights[src_index]
                weights[src_index] = 0

        assert qubit < num_qubits

        # print(f"qubit: {qubit}, control: {control:b}, control_states: {control_states}, theta: {theta}, weights: {weights}")

        control_qubits = [circuit.qubit_at(i) for i, _ in control_states]
        phases = [phase for _, phase in control_states]

        if direction == 1:
            theta = -np.pi
            gate = MCRY(theta, control_qubits, phases, circuit.qubit_at(qubit))
            mcry_gates.append(gate)

        if direction == 2:
            if len(thetas) == 0:
                assert False, "no theta found"
            elif len(thetas) == 1:
                theta = list(thetas.keys())[0]
                gate = MCRY(theta, control_qubits, phases, circuit.qubit_at(qubit))
                mcry_gates.append(gate)
            else:
                print(f"thetas = {thetas}")
                
                # This is an exception case, we need to split the gate
                
                if len(thetas) == 2:
                    state1, state2 = list(thetas.values())


                    decision_variable: int = int(np.floor(np.log2(state1 ^ state2)))
                    
                    phase1 = (int(state1) >> decision_variable) & 1
                    phase2 = (int(state2) >> decision_variable) & 1

                    control_qubits.append(circuit.qubit_at(decision_variable))
                    
                    phases1 = phases + [phase1]
                    phases2 = phases + [phase2]

                    theta1 = list(thetas.keys())[0]
                    theta2 = list(thetas.keys())[1]


                    if len(control_qubits) == 1:
                        # special case
                        gate = MULTIPLEXY(theta1, theta2, control_qubits[0], circuit.qubit_at(qubit))
                        mcry_gates.append(gate)
                        
                    else:
                        gate1 = MCRY(theta1, control_qubits, phases1, circuit.qubit_at(qubit))
                        gate2 = MCRY(theta2, control_qubits, phases2, circuit.qubit_at(qubit))
                        mcry_gates.append(gate1)
                        mcry_gates.append(gate2)
                else:
                    raise NotImplementedError

    
    for gate in mcry_gates[::-1]:

        circuit.add_gate(gate)
        continue

        if circuit.has_mcry():
            circuit.mcry(theta, control_qubits, circuit.qr[qubit])
        
        else:
            if len(control_qubits) == 0:
                circuit.ry(theta, circuit.qr[qubit])
                continue
            
            # we prepare the rotation table
            rotation_table = np.zeros(2 ** (len(control_qubits)))

            rotated_index = 0
            for i, value_tuple in enumerate(control_qubits):
                _, controlled_by_one = value_tuple
                if controlled_by_one == True:
                    rotated_index += 2 ** i


            # only rotate the target qubit if the control qubits are in the positive phase
            rotation_table[rotated_index] = theta

            # print(f"rotation table = {rotation_table}")
            # print(f"control qubits = {control_qubits}")

            control_sequence = synthesize_multi_controlled_rotations(rotation_table)
            # print(f"control sequence = {control_sequence}")


            control_qubits = [
                qubit for qubit, _ in control_qubits
            ]
            apply_control_sequence_to_y(
                circuit, control_sequence, control_qubits, circuit.qr[qubit]
            )

    circuit.flush()
    circuit.measure()

    return circuit