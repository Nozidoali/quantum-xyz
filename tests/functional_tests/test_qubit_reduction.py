#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 13:24:00
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 13:33:37
"""

# pylint: skip-file


from xyz import qubit_reduction
from xyz import QCircuit
from xyz import D_state
from xyz import quantize_state


def test_qubit_reduction():
    """Test the qubit reduction of a 3D circuit ."""
    circuit = QCircuit(3)
    state = quantize_state(D_state(3, 1))
    qubit_reduction(circuit, state)


if __name__ == "__main__":
    test_qubit_reduction()
