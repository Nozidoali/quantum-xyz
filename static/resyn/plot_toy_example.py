#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-24 10:16:07
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-24 16:17:57
"""

import xyz
import numpy as np

from qiskit_ibm_runtime import EstimatorV2 as Estimator, QiskitRuntimeService
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler

from qiskit import qasm2

if __name__ == "__main__":
    # circuit = xyz.QCircuit(3, map_gates=True)

    # circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(0)))
    # circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(0), True, xyz.QBit(1)))
    # circuit.add_gate(
    #     xyz.MCRY(np.pi, [xyz.QBit(0), xyz.QBit(1)], [True, False], xyz.QBit(2))
    # )
    # circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(1)))
    # # circuit.add_gate(xyz.X(xyz.QBit(1)))
    # circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(1), True, xyz.QBit(2)))

    # print(xyz.to_tikz(circuit))

    circuit = xyz.QCircuit(3, map_gates=False)

    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(0)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(0), True, xyz.QBit(1)))
    circuit.add_gate(
        xyz.MCRY(np.pi, [xyz.QBit(0), xyz.QBit(1)], [True, False], xyz.QBit(2))
    )
    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(1)))
    # circuit.add_gate(xyz.X(xyz.QBit(1)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(1), True, xyz.QBit(2)))

    windows = xyz.extract_windows_naive(circuit)
    new_circuit = xyz.QCircuit(3, map_gates=True)

    # now let us manully re-order the windows
    intermediate_state = xyz.quantize_state([0.5, 0.5, 0.5, 0.5, 0, 0, 0, 0])
    new_circuit.add_gates(
        xyz.resynthesize_window(*windows[0]),
    )
    new_circuit.add_gates(
        xyz.resynthesize_window(
            xyz.QBit(1),
            windows[1][1] + windows[3][1],
            windows[0][3],
            intermediate_state,
        ),
    )
    # new_circuit.add_gates(
    #     xyz.resynthesize_window(
    #         xyz.QBit(2),
    #         windows[2][1] + windows[4][1],
    #         intermediate_state,
    #         final_state,),
    # )
    new_circuit.add_gates(
        [
            xyz.RY(np.pi / 4, xyz.QBit(2)),
            xyz.CX(xyz.QBit(1), True, xyz.QBit(2)),
            xyz.RY(-np.pi / 2, xyz.QBit(2)),
            xyz.CX(xyz.QBit(0), True, xyz.QBit(2)),
            xyz.RY(np.pi / 4, xyz.QBit(2)),
        ]
    )
    # new_circuit = xyz.resynthesis(circuit)

    # print(xyz.to_qiskit(new_circuit))

    # state_vector = xyz.simulate_circuit(new_circuit)
    # print(xyz.quantize_state(state_vector))

    print(xyz.to_tikz(new_circuit))
