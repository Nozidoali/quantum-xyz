#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-16 15:19:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-16 15:27:39
"""

import numpy as np
import xyz
import json


def test_mcmy_mapping(num_qubits: int = 3):
    circuit = xyz.QCircuit(num_qubits, map_gates=True)

    control_qubits = [circuit.qubit_at(i) for i in range(num_qubits - 1)]
    control_phases = [0 for i in range(num_qubits - 1)]

    gate = xyz.MCRY(
        0.5 * np.pi, control_qubits, control_phases, circuit.qubit_at(num_qubits - 1)
    )

    circuit.add_gate(gate)

    # get CX cost
    cx_cost = circuit.get_cnot_cost()

    print(f"num_qubits: {num_qubits}, cx_cost: {cx_cost}")

    return cx_cost


if __name__ == "__main__":
    # try to find the polynomial relationship between the number of qubits and the cost of the circuit
    datas = {i - 1: test_mcmy_mapping(i) for i in range(3, 30)}

    print(json.dumps(datas, indent=4))
