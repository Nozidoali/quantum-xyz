#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-15 13:14:21
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-15 14:32:11
"""

import numpy as np

from xyz.circuit import QCircuit, RY
from xyz.qstate import QState
from xyz.utils import stopwatch

from ._exact_cnot_synthesis import exact_cnot_synthesis
from ._sparse_state_synthesis import density_reduction
from ._ground_state_calibration import ground_state_calibration
from ._support_reduction import support_reduction
from ._qubit_decomposition import (
    select_pivot_qubit,
    to_controlled_gate,
    qubit_decomposition_opt,
)

ENABLE_QUBIT_REDUCTION = True
ENABLE_DENSITY_REDUCTION = True
ENABLE_EXACT_SYNTHESIS = True
ENABLE_DECOMPOSITION = False

class HybridCnotSynthesisStatistics:
    """Classes the hybridCnothesisStatistics class .
    """
    def __init__(self) -> None:
        self.time_total: float = 0
        self.num_runs_support_reduction: int = 0
        self.time_support_reduction: float = 0
        self.time_exact_cnot_synthesis: float = 0
        self.time_density_reduction: float = 0
        self.time_qubit_decomposition: float = 0

    def report(self):
        """Report the number of runs supported by the benchmark .
        """
        print("-" * 80)
        print(f"time_total: {self.time_total}")
        print("-" * 80)
        print(f"num_runs_support_reduction: {self.num_runs_support_reduction}")
        print(f"time_support_reduction: {self.time_support_reduction}")
        print(f"time_exact_cnot_synthesis: {self.time_exact_cnot_synthesis}")
        print(f"time_density_reduction: {self.time_density_reduction}")
        print(f"time_qubit_decomposition: {self.time_qubit_decomposition}")
        print("-" * 80)
        

def _hybrid_cnot_synthesis_impl(
    circuit: QCircuit,
    state: QState,
    stats: HybridCnotSynthesisStatistics = None,
):
    # first, run support reduction
    with stopwatch("support_reduction") as timer:
        state, support_reducing_gates = support_reduction(circuit, state, enable_cnot=True)
    
    if stats is not None:
        stats.num_runs_support_reduction += 1
        stats.time_support_reduction += timer.time()


    # get the states
    supports = state.get_supports()
    num_supports = len(supports)
    density = state.get_sparsity()

    # check for the trivial case
    if density == 1:
        ground_state_calibration_gates = ground_state_calibration(circuit, state)

        gates = []
        for gate in ground_state_calibration_gates:
            gates.append(gate)
        for gate in support_reducing_gates:
            gates.append(gate)

        return gates

    # exact synthesis
    if ENABLE_EXACT_SYNTHESIS and num_supports <= 4:
        try:
            with stopwatch("exact_cnot_synthesis") as timer:
                exact_gates = exact_cnot_synthesis(
                    circuit,
                    state,
                    optimality_level=3,
                    verbose_level=0,
                    cnot_limit=7,
                )
            if stats is not None:
                stats.time_exact_cnot_synthesis += timer.time()
                
            gates = []
            for gate in exact_gates:
                gates.append(gate)
            for gate in support_reducing_gates:
                gates.append(gate)

            return gates
        except ValueError:
            pass

    # sparse state synthesis
    if ENABLE_DENSITY_REDUCTION:
        with stopwatch("density_reduction") as timer:
            new_state, density_reduction_gates = density_reduction(
                circuit, state, verbose_level=0
            )
        if stats is not None:
            stats.time_density_reduction += timer.time()
            
        rec_gates = _hybrid_cnot_synthesis_impl(
            circuit,
            new_state,
            stats=stats,
        )

        sparse_qsp_gates = []
        for gate in rec_gates:
            sparse_qsp_gates.append(gate)
        for gate in density_reduction_gates:
            sparse_qsp_gates.append(gate)
        for gate in support_reducing_gates:
            sparse_qsp_gates.append(gate)

    # qubit decomposition
    if ENABLE_QUBIT_REDUCTION:
        with stopwatch("qubit_decomposition") as timer:
            qubit_decomposition_gates, new_state = qubit_decomposition_opt(
                circuit, state, supports
            )
        if stats is not None:
            stats.time_qubit_decomposition += timer.time()

        rec_gates = _hybrid_cnot_synthesis_impl(
            circuit,
            new_state,
            stats=stats,
        )

        qubit_reduction_gates = []
        for gate in rec_gates:
            qubit_reduction_gates.append(gate)
        for gate in qubit_decomposition_gates:
            qubit_reduction_gates.append(gate)
        for gate in support_reducing_gates:
            qubit_reduction_gates.append(gate)

    if ENABLE_DECOMPOSITION:
        pivot = select_pivot_qubit(state, supports)
        pivot_qubit = circuit.qubit_at(pivot)

        neg_state, pos_state, weights0, weights1 = state.cofactors(pivot)

        # we first add a rotation gate to the pivot qubit
        theta = 2 * np.arccos(np.sqrt(weights0 / (weights0 + weights1)))
        ry_gate = RY(theta, pivot_qubit)

        pos_gates = _hybrid_cnot_synthesis_impl(
            circuit,
            pos_state,
            stats=stats,
        )

        neg_gates = _hybrid_cnot_synthesis_impl(
            circuit,
            neg_state,
            stats=stats,
        )

        qubit_decomposition_gates = []
        qubit_decomposition_gates.append(ry_gate)
        for gate in pos_gates:
            controlled_gate = to_controlled_gate(gate, pivot_qubit, True)
            qubit_decomposition_gates.append(controlled_gate)

        for gate in neg_gates:
            controlled_gate = to_controlled_gate(gate, pivot_qubit, False)
            qubit_decomposition_gates.append(controlled_gate)

        for gate in support_reducing_gates:
            qubit_decomposition_gates.append(gate)

    # we choose the best one
    candidates = []

    if ENABLE_DENSITY_REDUCTION:
        candidates.append(sparse_qsp_gates)
    if ENABLE_QUBIT_REDUCTION:
        candidates.append(qubit_reduction_gates)
    if ENABLE_DECOMPOSITION:
        candidates.append(qubit_decomposition_gates)

    # pylint: disable=unnecessary-lambda
    best_gates = min(candidates, key=lambda gates: len(gates))

    return best_gates


def hybrid_cnot_synthesis(
    state: QState,
    map_gates: bool = False,
    stats: HybridCnotSynthesisStatistics = None,
):
    """Return a QCircuit that can be used to construct a circuit that can be used to compute the non - linear correlation coefficients .

    :param state: [description]
    :type state: QState
    :param map_gates: [description], defaults to False
    :type map_gates: bool, optional
    :return: [description]
    :rtype: [type]
    """
    circuit = QCircuit(state.num_qubits, map_gates=map_gates)
    
    with stopwatch("hybrid_cnot_synthesis") as timer:
        gates = _hybrid_cnot_synthesis_impl(
            circuit,
            state,
            stats=stats,
        )
    
    stats.time_total = timer.time()
    
    circuit.add_gates(gates)
    return circuit
