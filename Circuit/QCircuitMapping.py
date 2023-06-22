#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 22:43:37
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 00:14:40
'''

from typing import List
from .Gates import *

from .QCircuitQiskitCompatible import *
from Utils import *

def control_sequence_to_gates(
    control_sequence: list, control_qubits: List[QBit], target_qubit: QBit
) -> List[QGate]:
    
    gates: List[QGate] = []
    
    for control in control_sequence:
        rotation_theta, control_id = control

        gates.append(RY(rotation_theta, target_qubit))
        gates.append(CX(control_qubits[control_id], 1, target_qubit))

    return gates

def map_muxy(gate: MULTIPLEXY) -> List[QGate]:

    assert gate.type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]

    control_sequence = synthesize_multi_controlled_rotations(rotation_table)

    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubit], gate.target_qubit
    )

    return gates

def map_mcry(gate: QGate) -> List[QGate]:

    match gate.type:
        
        case QGateType.MCRY:
            
            control_qubits = gate.control_qubits
            phases = gate.phases
            target_qubit = gate.target_qubit

        case QGateType.CRY:

            control_qubits = [gate.control_qubit]
            phases = [gate.phase]
            target_qubit = gate.target_qubit
        
        case _:
            raise Exception('Not a MCRY gate')
    
    # we prepare the rotation table
    rotation_table = np.zeros(2 ** (len(control_qubits)))

    rotated_index = 0
    for i, controlled_by_one in enumerate(phases):
        if controlled_by_one == True:
            rotated_index += 2 ** i

    # only rotate the target qubit if the control qubits are in the positive phase
    rotation_table[rotated_index] = gate.theta

    control_sequence = synthesize_multi_controlled_rotations(rotation_table)

    gates = control_sequence_to_gates(
        control_sequence, control_qubits, target_qubit
    )

    for gate in gates:
        print(f"Generated gate: {gate}")

    return gates


class QCircuitMapping(QCircuitQiskitCompatible):

    def __init__(self) -> None:
        super().__init__()
        self.do_mapping: bool = True

    def add_gate(self, gate: QGate) -> None:

        if not self.do_mapping:
            super().add_gate(gate)
            return
        
        match gate.type:

            case QGateType.MULTIPLEX_Y:
                gates = map_muxy(gate)
                self.add_gates(gates)

            case QGateType.MCRY:
                gates = map_mcry(gate)
                self.add_gates(gates)
                
            case QGateType.CRY:
                gates = map_mcry(gate)
                self.add_gates(gates)

            case _:
                super().add_gate(gate)

    def add_gates(self, gates: List[QGate]) -> None:
        '''
        Add a list of gates to the circuit, with optimization
        '''
        for gate in gates:
            self.add_gate(gate)

    def set_mapping(self, do_mapping: bool) -> None:
        self.do_mapping = do_mapping