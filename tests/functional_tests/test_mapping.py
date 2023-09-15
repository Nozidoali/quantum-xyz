#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-13 10:09:07
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-13 10:11:20
"""

# pylint: skip-file

import numpy as np
from qiskit import Aer, transpile
import xyz


def test_mapping():
    """Test that tests the mapping of the QCircuit ."""
    circuit = xyz.QCircuit(5, map_gates=True)

    circuit.add_gate(
        xyz.MCRY(
            np.pi / 2,
            [
                circuit.qubit_at(1),
                circuit.qubit_at(2),
                circuit.qubit_at(3),
                circuit.qubit_at(4),
            ],
            [1, 1, 1, 0],
            circuit.qubit_at(0),
        )
    )

    circuit = circuit.to_qiskit()
    print(circuit)
    circuit = transpile(circuit, basis_gates=["cx", "u", "cu"], optimization_level=3)


if __name__ == "__main__":
    test_mapping()
