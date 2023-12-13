#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-21 22:40:17
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-21 23:43:54
"""

from xyz.circuit import QCircuit
from xyz.qstate import QState
from .library import DefaultLibrary, Library


def cnot_synthesis(
    circuit: QCircuit,
    state: QState,
    library: Library = DefaultLibrary(),
    verbose_level: int = 0,
):
    """Computes the scnothesis of a circuit .

    :param circuit: [description]
    :type circuit: QCircuit
    :param state: [description]
    :type state: QState
    :param library: [description], defaults to DefaultLibrary()
    :type library: Library, optional
    :return: [description]
    :rtype: [type]
    """
    library.initialize_queue(state, circuit)
    library.explore()
    gates = library.get_solution()
    return gates
