#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-04-02 14:09:25
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-02 14:35:48
'''

# pylint: skip-file

from .build.bindings.xyz import initialize as _initialize
from ..circuit import *
from ..qstate import QState

import re

class CBridge:
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def _to_circuit(circuit_str: str):
        gates = []
        circuit = None
        for line in circuit_str.split("\n"):
            if line.startswith("#") or len(line) == 0:
                continue
            if line.startswith("qreg"):
                n_qubits = int(line.split(" ")[1])
                circuit = QCircuit(n_qubits)
                continue
            try:
                gate = CBridge._to_gate(circuit, line)
                gates.append(gate)
            except:
                raise ValueError(f"Invalid gate: {line}")
        for gate in gates:
            circuit.add_gate(gate)
        return circuit
    
    @staticmethod
    def _to_gate(circuit: QCircuit, gate_str: str):
        
        if circuit is None:
            raise ValueError("The circuit is not initialized.")
        
        gate_str = gate_str.replace(" ", "")
        
        control_qubits = []
        phases = []
        
        # get the control qubits in the C[] 
        if gate_str.startswith("C"):
            # find the str between the brackets
            control_str = re.search(r'\[(.*?)\]', gate_str).group(1)
            # get the control qubits
            control_qubits = [int(qubit) for qubit in control_str.split(",")]
            
            phases = [qubit > 0 for qubit in control_qubits]
            control_qubits = [circuit.qubit_at(abs(qubit)) for qubit in control_qubits]
    
            gate_str = gate_str.split("]")[1]
        
        # the rest are the normal gates
        gate_name = gate_str.split("(")[0]
        
        # get info inside the parentheses
        info_str = re.search(r'\((.*?)\)', gate_str).group(1)
        infos = info_str.split(",")
        
        # rotation gates
        if gate_name.startswith("R"):
            target_qubit, theta = circuit.qubit_at(int(infos[0])), float(infos[1])
            if gate_name == "RY":
                if len(control_qubits) > 1:
                    return MCRY(theta, control_qubits, phases, target_qubit)
                elif len(control_qubits) == 1:
                    return CRY(theta, control_qubits[0], phases[0], target_qubit)
                else:
                    return RY(theta, target_qubit)
            else:
                raise NotImplementedError("Rotation gates other than RY is not supported.")

        # pauli gates
        else:
            target_qubit = circuit.qubit_at(int(infos[0]))
            if gate_name == "X":
                if len(control_qubits) > 1:
                    raise NotImplementedError("Multiple control qubits for X gate is not supported.")
                elif len(control_qubits) == 1:
                    return CX(control_qubits[0], phases[0], target_qubit)
                else:
                    return X(target_qubit)
            else:
                raise NotImplementedError("Pauli gates other than X is not supported.")
    
def initialize(state: QState) -> QCircuit:
    circuit_str = _initialize(state)
    return CBridge._to_circuit(circuit_str)