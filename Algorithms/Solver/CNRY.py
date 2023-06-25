#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-21 14:02:46
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 13:08:41
'''

import numpy as np

from typing import List

from Circuit import *

from Algorithms.Decompose import *

from .SolverImpl import *
from Visualization import *
import logging


def cnry_solver(final_state: np.ndarray):

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler("cnry_solver.log")
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    solver = CnRYSolver(final_state)
    solver.solve()
    solution = solver.retrieve_solution()

    return solution

def solution_to_circuit(num_qubits: int, solution: list) -> QCircuit:

    circuit = QCircuit(num_qubits)
    circuit.set_mapping(True)

    weights = np.zeros(1 << num_qubits)

    mcry_gates = []

    idx: int = 0

    for step in solution:

        states: CnRyState
        move: CnRyMove
        states, move = step

        # save the figure
        if num_qubits == 3 and False:
            print_cube(states.states, f"step_{idx}.pdf")
        idx += 1
        
        if move is None:

            # this is the initial state
            # we initialize the weights
            for state in states.states:
                weights[state] = 1
            continue
        
        qubit: int = move.pivot_qubit
        control: int = move.control_state
        direction: int = move.direction
        control_states: List[int] = move.control_states

        print(f"qubit: {qubit}, control: {control:b}, direction: {direction}, control_states: {control_states}")

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
            
            
            if direction == CnRYDirection.SWAP:

                # we need to figure out which bit is the src and which bit is the dst
                if weights[neg_index] == 0:
                    src_index = pos_index
                    dst_index = neg_index
                else:
                    src_index = neg_index
                    dst_index = pos_index

                # we need to flip the bit (from the src to dst)
                # assert weights[dst_index] == 0
                weights[dst_index], weights[src_index] = weights[src_index], weights[dst_index]

            if direction == CnRYDirection.MERGE:

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

        control_qubits = [circuit.qubit_at(i) for i, _ in control_states]
        phases = [phase for _, phase in control_states]

        if direction == CnRYDirection.SWAP:
            theta = -np.pi
            gate = MCRY(theta, control_qubits, phases, circuit.qubit_at(qubit))
            mcry_gates.append(gate)

        if direction == CnRYDirection.MERGE:
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