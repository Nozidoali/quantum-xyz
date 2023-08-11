#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 13:24:31
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:39:10
"""

# standard library
from typing import List

# third party library
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# my own library
from .gates import QBit, QGate, QGateType
from .qiskit_gates import SpecialGates


def _to_qiskit(
    self, with_measurement: bool = True, with_tomography: bool = False
) -> QuantumCircuit:
    """Convert this circuit to a QuantumCircuit .

    :param with_measurement: [description], defaults to True
    :type with_measurement: bool, optional
    :param with_tomography: [description], defaults to False
    :type with_tomography: bool, optional
    :return: [description]
    :rtype: QuantumCircuit
    """
    num_qubits = self.get_num_qubits()

    quantum_registers = QuantumRegister(num_qubits)
    classical_registers = ClassicalRegister(num_qubits)

    if not with_tomography:
        circuit = QuantumCircuit(quantum_registers, classical_registers)
    else:
        circuit = QuantumCircuit(quantum_registers)

    def _to_register(qubit: QBit | List[QBit]) -> QuantumRegister:
        nonlocal quantum_registers
        if isinstance(qubit, QBit):
            return quantum_registers[qubit.index]
        if isinstance(qubit, list):
            return [quantum_registers[q.index] for q in qubit]

    gate: QGate
    for gate in self.get_gates():
        match gate.get_qgate_type():
            case QGateType.MCRY:
                special_gate = SpecialGates.mcry(gate)
                circuit.append(
                    special_gate,
                    _to_register(gate.control_qubits + [gate.target_qubit]),
                )

            case QGateType.CX:
                circuit.cx(
                    _to_register(gate.control_qubit),
                    _to_register(gate.target_qubit),
                    ctrl_state=gate.phase,
                )

            case QGateType.RY:
                circuit.ry(gate.theta, _to_register(gate.target_qubit))

            case QGateType.Z:
                circuit.z(_to_register(gate.target_qubit))

            case QGateType.X:
                circuit.x(_to_register(gate.target_qubit))

            case QGateType.CRY:
                circuit.cry(
                    gate.theta,
                    _to_register(gate.control_qubit),
                    _to_register(gate.target_qubit),
                    ctrl_state=gate.phase,
                )

    if with_measurement:
        circuit.measure(quantum_registers, classical_registers)
        return circuit

    if with_tomography:
        return circuit

    return circuit
