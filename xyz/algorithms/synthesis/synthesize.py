#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 10:36:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 11:02:26
"""


import logging
from sys import stdout

import numpy as np
from scipy import sparse

from xyz.utils.colors import print_green
from .exact_cnot_synthesis import exact_cnot_synthesis

from xyz.circuit import QCircuit
from xyz.srgraph import quantize_state
from xyz.srgraph.operators.qstate.qstate import QState

from .qubit_reduction import qubit_reduction
from .qubit_decomposition import qubit_decomposition
from .sparse_state_synthesis import sparse_state_synthesis, density_reduction
from .ground_state_calibration import ground_state_calibration
from .support_reduction import support_reduction

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
    state: QState,
    optimality_level: int = 3,
    map_gates: bool = False,
    verbose_level: int = 0,
    runtime_limit: int = None,
):
    """
    @brief Runs the search based state synthesis
    @param verbose_level Whether to print out the state of the search
    """

    log = intialize_logger()

    num_qubits = state.num_qubits

    # initialize the circuit
    circuit = QCircuit(num_qubits, map_gates=map_gates)
    post_processing_gates = []
    pre_processing_gates = []

    # reduce the number of qubits
    if optimality_level <= 0:
        gates = qubit_reduction(circuit, state, optimality_level)
        for gate in gates[::-1]:
            post_processing_gates.append(gate)

    # deep copy
    curr_state = QState(state.index_to_weight, state.num_qubits)

    gates = []
    
    skip_exact_cnot_synthesis: bool = False
    
    while True:
        density = len(curr_state.index_set)
        
        if verbose_level >= 3:
            print(f"Current state: {curr_state}, density: {density}")

        # we reach the end of the state
        if density == 1:
            
            _gates = ground_state_calibration(circuit, curr_state)
            for gate in _gates:
                pre_processing_gates.append(gate)
            break
        
        num_supports = len(curr_state.get_supports())
        if not skip_exact_cnot_synthesis and num_supports <= 4:
            try:
                print(f"running exact cnot synthesis with optimality_level={optimality_level}", end="...")
                stdout.flush()
                _gates = exact_cnot_synthesis(
                    circuit,
                    curr_state,
                    optimality_level=optimality_level,
                    verbose_level=verbose_level,
                    runtime_limit=runtime_limit,
                )
                print_green(f"done")
                for gate in _gates:
                    gates.append(gate)
                    
                break
            except ValueError:
                skip_exact_cnot_synthesis = True
                pass


        complexity_estimation = (1 << num_supports) * curr_state.get_sparsity()
        OPTIZATION_COMPLEXITY2 = 1 << 8
        OPTIZATION_COMPLEXITY1 = 1 << 10
        if complexity_estimation <= OPTIZATION_COMPLEXITY2:
            try:
                # we can use optimality_level=2
                exact_gates = exact_cnot_synthesis(
                    circuit,
                    curr_state,
                    optimality_level=2,
                    verbose_level=verbose_level,
                    runtime_limit=runtime_limit,
                )
                for gate in exact_gates:
                    gates.append(gate)
                break
            except ValueError:
                skip_exact_cnot_synthesis = True
                pass
        if complexity_estimation <= OPTIZATION_COMPLEXITY1:
            # we can use optimality_level=1
            try:
                exact_gates = exact_cnot_synthesis(
                    circuit,
                    curr_state,
                    optimality_level=1,
                    verbose_level=verbose_level,
                    runtime_limit=runtime_limit,
                )
                for gate in exact_gates:
                    gates.append(gate)
                break
            except ValueError:
                skip_exact_cnot_synthesis = True
                pass
            
        print(f"reducing density", end="...")
        stdout.flush()
        new_state, _gates = density_reduction(circuit, curr_state, verbose_level=verbose_level)
        print_green(f"done")
        
        print(f"reducing supports", end="...")
        stdout.flush()
        support_reduced_state, support_reduction_gates = support_reduction(circuit, new_state)
        print_green(f"done")
        
        for gate in _gates:
            post_processing_gates.append(gate)
            
        for gate in support_reduction_gates:
            post_processing_gates.append(gate)

        curr_state = support_reduced_state
        


    # gates = qubit_decomposition(
    #     circuit, state, optimality_level, verbose_level, runtime_limit=runtime_limit
    # )
    
    for gate in pre_processing_gates:
        circuit.add_gate(gate)

    for gate in gates:
        circuit.add_gate(gate)

    for gate in post_processing_gates[::-1]:
        circuit.add_gate(gate)

    return circuit
