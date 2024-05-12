#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-26 09:35:58
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-05 18:59:23
"""

import xyz
import numpy as np

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit import qasm2, transpile


def run_qiskit(circuit: xyz.QCircuit, state_vector: np.ndarray, data={}):
    n_qubits = circuit.get_num_qubits()
    backend = GenericBackendV2(num_qubits=n_qubits)
    pass_manager = generate_preset_pass_manager(
        optimization_level=3, backend=backend, basis_gates=["cx", "ry", "z"]
    )
    qc = xyz.to_qiskit(circuit)
    with xyz.stopwatch("qiskit") as timer_qiskit:
        qc_opt = pass_manager.run(qc)
    # print(qc_opt.count_ops())
    # print(qc_opt)
    # print()
    n_total = sum(qc_opt.count_ops().values())
    data["n_g2_qiskit"] = qc_opt.count_ops().get("cx", 0)
    data["n_g_qiskit"] = n_total - data["n_g2_qiskit"]
    data["time_qiskit"] = timer_qiskit.time()

    return qc_opt


if __name__ == "__main__":
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(0)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(0), True, xyz.QBit(1)))
    circuit.add_gate(
        xyz.MCRY(np.pi, [xyz.QBit(0), xyz.QBit(1)], [True, False], xyz.QBit(2))
    )
    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(1)))
    # circuit.add_gate(xyz.X(xyz.QBit(1)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(1), True, xyz.QBit(2)))

    new_circuit = xyz.resynthesis(circuit, verbose_level=2)
    print(xyz.to_qiskit(new_circuit))

    state = xyz.QState.ground_state(3)
    for gate in new_circuit.get_gates():
        print(gate)
        state = gate.apply(state)
        print(state)

    # state_vector = xyz.simulate_circuit(new_circuit)
    # new_circuit_qsp = xyz.prepare_state(state_vector, map_gates=True)
    # print(xyz.to_qiskit(new_circuit_qsp))
    # new_circuit_qiskit = run_qiskit(new_circuit, state_vector)
    # print(new_circuit_qiskit)
