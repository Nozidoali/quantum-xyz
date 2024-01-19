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

from xyz.utils.colors import print_green

from xyz.circuit import QCircuit
from xyz.qstate import QState

from ._exact_cnot_synthesis import exact_cnot_synthesis
from ._qubit_reduction import qubit_reduction
from ._sparse_state_synthesis import density_reduction
from ._ground_state_calibration import ground_state_calibration
from ._support_reduction import support_reduction
from ._qubit_decomposition import qubit_decomposition


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
    cnot_limit: int = None,
    reduction_method: str = "qubit",
) -> QCircuit:
    """
    @brief Runs the search based state synthesis
    @param verbose_level Whether to print out the state of the search
    """

    num_qubits = state.num_qubits

    # initialize the circuit
    circuit = QCircuit(num_qubits, map_gates=map_gates)

    if reduction_method == "qubit":
        gates = qubit_decomposition(
            circuit, state, optimality_level, verbose_level, cnot_limit=cnot_limit
        )
        circuit.add_gates(gates)
        return circuit

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
                if verbose_level >= 2:
                    print(
                        f"running exact cnot synthesis with optimality_level={optimality_level}",
                        end="...",
                    )
                stdout.flush()
                _gates = exact_cnot_synthesis(
                    circuit,
                    curr_state,
                    optimality_level=optimality_level,
                    verbose_level=verbose_level,
                    cnot_limit=cnot_limit,
                )
                if verbose_level >= 2:
                    print_green("done")
                for gate in _gates:
                    gates.append(gate)

                break
            except ValueError:
                skip_exact_cnot_synthesis = True

        if verbose_level >= 2:
            print(f"reducing density, current density = {density}", end="...")
        stdout.flush()
        new_state, _gates = density_reduction(
            circuit, curr_state, verbose_level=verbose_level
        )
        if verbose_level >= 2:
            print_green("done")

        for gate in _gates:
            post_processing_gates.append(gate)

        if verbose_level >= 2:
            print(f"reducing supports, num_supports = {num_supports}", end="...")
        stdout.flush()
        support_reduced_state, support_reduction_gates = support_reduction(
            circuit, new_state
        )
        curr_state = support_reduced_state
        num_supports: int = len(curr_state.get_supports())
        if verbose_level >= 2:
            print_green(f"done, num_supports = {num_supports}")

        for gate in support_reduction_gates:
            post_processing_gates.append(gate)

    for gate in pre_processing_gates:
        circuit.add_gate(gate)

    for gate in gates:
        circuit.add_gate(gate)

    for gate in post_processing_gates[::-1]:
        circuit.add_gate(gate)

    return circuit
