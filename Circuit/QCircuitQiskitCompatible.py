#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-22 13:24:31
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:01:45
'''

from .Gates import *
from .QCircuitBase import *
from .QCircuitOptimized import *
from .Qiskit import *

from qiskit.circuit.library.standard_gates import *
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

class QCircuitQiskitCompatible(QCircuitOptimized):
    
    def __init__(self) -> None:
        super().__init__()
    
    def to_qiskit(self, with_measurement: bool = False) -> QuantumCircuit:
        
        num_qubits = self.get_num_qubits()

        qr = QuantumRegister(num_qubits)
        cr = ClassicalRegister(num_qubits)

        circuit = QuantumCircuit(qr, cr)

        def map(qubit: QBit | List[QBit]):
            nonlocal qr
            if isinstance(qubit, QBit):
                return qr[qubit.index]
            elif isinstance(qubit, list):
                return [qr[q.index] for q in qubit]

        for gate in self.get_gates():
            
            match gate.type:
                case QGateType.MCRY:

                    special_gate = SpecialGates.mcry(gate)
                    circuit.append(
                        special_gate, 
                        map(gate.control_qubits + [gate.target_qubit]))
                    
                case QGateType.CX:
                    circuit.cx(
                        map(gate.control_qubit), 
                        map(gate.target_qubit))

                case QGateType.RY:
                    circuit.ry(
                        gate.theta, 
                        map(gate.target_qubit))
                
        if with_measurement:
            circuit.measure(qr, cr)

        return circuit