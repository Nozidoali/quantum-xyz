#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-05 18:53:10
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-05 18:59:51
"""

import xyz
import numpy as np

if __name__ == "__main__":
    circuit = xyz.QCircuit(3, map_gates=True)

    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(0)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(0), True, xyz.QBit(1)))
    circuit.add_gate(
        xyz.MCRY(np.pi, [xyz.QBit(0), xyz.QBit(1)], [True, False], xyz.QBit(2))
    )
    state = xyz.simulate_circuit(circuit)
    print(xyz.quantize_state(state))
    circuit.add_gate(xyz.RY(np.pi / 2, xyz.QBit(1)))
    state = xyz.simulate_circuit(circuit)
    print(xyz.quantize_state(state))
    # circuit.add_gate(xyz.X(xyz.QBit(1)))
    circuit.add_gate(xyz.CRY(np.pi / 2, xyz.QBit(1), True, xyz.QBit(2)))

    new_circuit = xyz.resynthesis(circuit, verbose_level=2)
