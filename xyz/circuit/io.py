#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-22 16:49:19
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-22 16:49:37
"""

from .qcircuit import QCircuit


def to_qasm(circuit: QCircuit) -> str:
    """
    to_qasm:
    convert the circuit to qasm format
    """
    return circuit.to_qasm()
