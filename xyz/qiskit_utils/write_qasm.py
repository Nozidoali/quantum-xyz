#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-22 16:50:43
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-22 17:03:29
"""

from qiskit import qasm3, transpile
from ..circuit import QCircuit
from .to_qiskit import to_qiskit


def to_qasm(circuit: QCircuit) -> str:
    """
    write_qasm:
    write the circuit to qasm format
    """
    qc = to_qiskit(circuit)
    return qasm3.dumps(qc)


def write_qasm(circuit: QCircuit, filename: str):
    """
    write_qasm:
    write the circuit to qasm format
    """
    with open(filename, "w") as f:
        f.write(to_qasm(circuit))
