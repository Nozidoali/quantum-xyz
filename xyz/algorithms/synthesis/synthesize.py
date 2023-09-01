#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""


import logging

import numpy as np

from xyz.circuit import QCircuit
from xyz.srgraph import quantize_state

from .qubit_reduction import qubit_reduction
from .qubit_decomposition import qubit_decomposition


def intialize_logger():
    """Initialize the logger .

    :return: [description]
    :rtype: [type]
    """
    # create logger with 'spam_application'
    log = logging.getLogger("synthesis")
    log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # create file handler which logs even debug messages
    file_handler = logging.FileHandler("synthesis.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    return log


def cnot_synthesis(
    state_vector: np.ndarray, optimality_level: int = 3, verbose_level: int = 0
):
    """
    @brief Runs the search based state synthesis
    @param verbose_level Whether to print out the state of the search
    """

    log = intialize_logger()

    target_state = quantize_state(state_vector)
    num_qubits = target_state.num_qubits

    # initialize the circuit
    circuit = QCircuit(num_qubits)
    post_processing_gates = []

    # reduce the number of qubits
    if optimality_level <= 0:
        gates = qubit_reduction(circuit, target_state, optimality_level)
        for gate in gates[::-1]:
            post_processing_gates.append(gate)

    gates = qubit_decomposition(circuit, target_state, optimality_level, verbose_level)

    for gate in gates:
        circuit.add_gate(gate)

    for gate in post_processing_gates:
        circuit.add_gate(gate)

    return circuit
