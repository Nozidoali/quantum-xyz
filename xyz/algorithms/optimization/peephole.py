#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2024-06-12 10:16:30
Last Modified by: Hanyu Wang
Last Modified time: 2024-06-12 10:17:00
'''

from xyz.circuit import QCircuit

def peephole_optimization(circuit: QCircuit) -> QCircuit:
    """
    peephole_optimization is a simple optimization technique that iteratively applies a set of rules to the circuit to reduce the number of gates.
    """
    return circuit