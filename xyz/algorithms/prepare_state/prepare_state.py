#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-15 13:14:21
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-15 14:32:11

Reference:
    @article{wang2024quantum,
        title={Quantum State Preparation Using an Exact CNOT Synthesis Formulation},
        author={Wang, Hanyu and Tan, Bochen and Cong, Jason and De Micheli, Giovanni},
        journal={arXiv preprint arXiv:2401.01009},
        year={2024}
    }
"""

from collections import namedtuple
from typing import List
import numpy as np


from xyz.circuit import QCircuit, RY, QGate
from xyz.qstate import QState, quantize_state
from xyz.utils import stopwatch
from xyz.utils import global_stopwatch_report
from xyz.utils import print_yellow

from ._exact_cnot_synthesis import exact_cnot_synthesis
from ._cardinality_reduction import cardinality_reduction
from ._ground_state_calibration import ground_state_calibration
from ._support_reduction import support_reduction
from ._qubit_decomposition import (
    select_pivot_qubit,
    to_controlled_gate,
    qubit_decomposition_opt,
)

EXACT_SYNTHESIS_QUBIT_THRESHOLD = 4
EXACT_SYNTHESIS_DENSITY_THRESHOLD = 10

EXACT_SYNTHESIS_CNOT_LIMIT = 10

ENABLE_EXACT_SYNTHESIS = True

ENABLE_QUBIT_REDUCTION = True
ENABLE_CARDINALITY_REDUCTION = True

ENABLE_DECOMPOSITION = False

ENABLE_REINDEX = True

ENABLE_PROGESS_BAR = True


class StatePreparationStatistics:
    """Classes the StatePreparationStatistics class ."""

    def __init__(self) -> None:
        self.time_total: float = 0
        self.num_runs_support_reduction: int = 0
        self.time_support_reduction: float = 0
        self.time_exact_cnot_synthesis: float = 0
        self.time_cardinality_reduction: float = 0
        self.time_qubit_decomposition: float = 0
        self.num_reduced_supports: int = 0
        self.num_reduced_density: int = 0
        self.num_saved_gates_decision: int = 0
        self.num_methods: dict = {}

    def report(self):
        """Report the number of runs supported by the benchmark ."""
        print("-" * 80)
        print(f"time_total: {self.time_total}")
        print("-" * 80)
        print(f"num_runs_support_reduction: {self.num_runs_support_reduction}")
        print(f"time_support_reduction: {self.time_support_reduction:0.02f} sec")
        print(f"time_exact_cnot_synthesis: {self.time_exact_cnot_synthesis:0.02f} sec")
        print(
            f"time_cardinality_reduction: {self.time_cardinality_reduction:0.02f} sec"
        )
        print(f"time_qubit_decomposition: {self.time_qubit_decomposition:0.02f} sec")
        print(f"num_reduced_supports: {self.num_reduced_supports}")
        print(f"num_reduced_density: {self.num_reduced_density}")
        print(f"num_saved_gates_decision: {self.num_saved_gates_decision}")
        print("-" * 80)
        for method, num in self.num_methods.items():
            print(f"{method}: {num}")
        print("-" * 80)


def _prepare_state_rec(
    circuit: QCircuit,
    state: QState,
    verbose_level: int = 0,
    stats: StatePreparationStatistics = StatePreparationStatistics(),
):
    prev_supports = state.get_supports()
    prev_num_supports = len(prev_supports)
    prev_density = state.get_sparsity()

    # first, run support reduction
    with stopwatch("support_reduction") as timer:
        state, support_reducing_gates = support_reduction(
            circuit, state, enable_cnot=True
        )
    num_cx_support_reduction = sum(
        (gate.get_cnot_cost() for gate in support_reducing_gates)
    )

    if ENABLE_REINDEX:
        # compact the state
        # now we get the sub state and sub circuit:
        sub_index_to_weight = {}
        old_to_new_qubit_mapping = {}

        supports = state.get_supports()
        num_supports = len(supports)
        for new_index, old_index in enumerate(supports):
            old_to_new_qubit_mapping[old_index] = new_index
        for index, weight in state.index_to_weight.items():
            new_index: int = 0
            for i, support in enumerate(supports):
                if index & (1 << support) != 0:
                    new_index |= 1 << i
            sub_index_to_weight[new_index] = weight
        state = QState(sub_index_to_weight, num_supports)
        circuit = circuit.sub_circuit(supports)

        # then we updates the supports to the new index
        supports = list(range(num_supports))

    # get the states
    supports = state.get_supports()
    num_supports = len(supports)
    cardinality = state.get_sparsity()

    if ENABLE_PROGESS_BAR:
        print(
            f"num_supports: {num_supports:5d}, cardinality: {cardinality:5d}", end="\r"
        )

    stats.num_runs_support_reduction += 1
    stats.time_support_reduction += timer.time()
    stats.num_reduced_supports += prev_num_supports - num_supports
    stats.num_reduced_density += prev_density - cardinality

    # check for the trivial case
    if cardinality == 1:
        ground_state_calibration_gates = ground_state_calibration(circuit, state)
        gates = ground_state_calibration_gates + support_reducing_gates
        # ground state calibration has 0 CNOT
        return gates, num_cx_support_reduction

    # exact synthesis
    if (
        ENABLE_EXACT_SYNTHESIS
        and num_supports <= EXACT_SYNTHESIS_QUBIT_THRESHOLD
        and cardinality <= EXACT_SYNTHESIS_DENSITY_THRESHOLD
    ):
        try:
            exact_gates = exact_cnot_synthesis(
                circuit,
                state,
                optimality_level=3,
                verbose_level=verbose_level,
                cnot_limit=EXACT_SYNTHESIS_CNOT_LIMIT,
            )
            if stats is not None:
                stats.time_exact_cnot_synthesis += timer.time()
            gates = exact_gates + support_reducing_gates
            num_cx_exact = sum((gate.get_cnot_cost() for gate in exact_gates))
            return gates, num_cx_exact
        except ValueError:
            pass

    # sparse state synthesis
    sparse_qsp_gates: List[QGate] = None
    num_sparse_qsp_cx: int = 0
    if ENABLE_CARDINALITY_REDUCTION:
        new_state, cardinality_reduction_gates = cardinality_reduction(
            circuit, state, verbose_level=0
        )
        num_cardinality_reduction_cx = sum(
            (gate.get_cnot_cost() for gate in cardinality_reduction_gates)
        )
        stats.time_cardinality_reduction += timer.time()
        rec_gates, rec_cx = _prepare_state_rec(
            circuit,
            new_state,
            stats=stats,
        )
        sparse_qsp_gates = (
            rec_gates + cardinality_reduction_gates + support_reducing_gates
        )
        num_sparse_qsp_cx = (
            rec_cx + num_cardinality_reduction_cx + num_cx_support_reduction
        )

    # qubit decomposition
    qubit_reduction_gates: List[QGate] = None
    num_qubit_reduction_cx: int = 0
    if ENABLE_QUBIT_REDUCTION:
        qubit_decomposition_gates, new_state = qubit_decomposition_opt(
            circuit, state, supports
        )
        num_qubit_reduction_cx = sum(
            (gate.get_cnot_cost() for gate in qubit_decomposition_gates)
        )
        stats.time_qubit_decomposition += timer.time()
        rec_gates, rec_cx = _prepare_state_rec(
            circuit,
            new_state,
            stats=stats,
        )
        qubit_reduction_gates = (
            rec_gates + qubit_decomposition_gates + support_reducing_gates
        )
        num_qubit_reduction_cx += rec_cx + num_cx_support_reduction

    qubit_decomposition_gates: List[QGate] = None
    num_qubit_decomposition_cx: int = 0  # not implemented yet
    if ENABLE_DECOMPOSITION:
        pivot = select_pivot_qubit(state, supports)
        pivot_qubit = circuit.qubit_at(pivot)
        neg_state, pos_state, weights0, weights1 = state.cofactors(pivot)
        # we first add a rotation gate to the pivot qubit
        theta = 2 * np.arctan(weights1 / weights0)
        ry_gate = RY(theta, pivot_qubit)
        pos_gates = _prepare_state_rec(
            circuit,
            pos_state,
            stats=stats,
        )
        neg_gates = _prepare_state_rec(
            circuit,
            neg_state,
            stats=stats,
        )

        qubit_decomposition_gates = [ry_gate]
        for gate in pos_gates:
            controlled_gate = to_controlled_gate(gate, pivot_qubit, True)
            qubit_decomposition_gates.append(controlled_gate)
        for gate in neg_gates:
            controlled_gate = to_controlled_gate(gate, pivot_qubit, False)
            qubit_decomposition_gates.append(controlled_gate)
        for gate in support_reducing_gates:
            qubit_decomposition_gates.append(gate)

    # we choose the best one
    # based on the number of CNOT gates
    Method = namedtuple("method", ["name", "gates", "num_gates"])
    candidates = []

    if sparse_qsp_gates is not None:
        candidates.append(Method("sparse_qsp", sparse_qsp_gates, num_sparse_qsp_cx))
    if qubit_reduction_gates is not None:
        candidates.append(
            Method("qubit_reduction", qubit_reduction_gates, num_qubit_reduction_cx)
        )
    if qubit_decomposition_gates is not None:
        candidates.append(
            Method(
                "qubit_decomposition",
                qubit_decomposition_gates,
                num_qubit_decomposition_cx,
            )
        )

    # pylint: disable=unnecessary-lambda
    best_candidate = min(candidates, key=lambda x: x.num_gates)
    worst_candidate = max(candidates, key=lambda x: x.num_gates)

    best_gates = best_candidate.gates
    best_method = best_candidate.name

    worst_num_gates = worst_candidate.num_gates
    best_num_gates = best_candidate.num_gates

    if stats is not None:
        stats.num_saved_gates_decision += worst_num_gates - best_num_gates
        stats.num_methods[best_method] = stats.num_methods.get(best_method, 0) + 1

    return best_gates, best_num_gates


def prepare_state(
    state: QState,
    map_gates: bool = True,
    verbose_level: int = 0,
    stats: StatePreparationStatistics = StatePreparationStatistics(),
) -> QCircuit:
    """A hybrid method combining both qubit- and cardinality- reduction.

    This is a wrapper for the _prepare_state_rec function.

    :param state: the target state to be prepared
    :type state: QState
    :param map_gates: map gates to {U2, CNOT}, this will take extra time, defaults to True
    :type map_gates: bool, optional
    :return: a quantum circuit
    :rtype: QCircuit
    """

    # check the input state
    if not isinstance(state, QState):
        if isinstance(state, np.ndarray):
            state = quantize_state(state)
        else:
            raise ValueError("state must be either a QState or a numpy array")

    # check the initial state
    num_qubits = state.num_qubits
    cardinality = state.get_sparsity()

    cardinality_reduction_cnot_estimation = int(cardinality * num_qubits)
    qubit_reduction_cnot_estimation = 1 << num_qubits

    # pylint: disable=W0603

    global ENABLE_QUBIT_REDUCTION
    global ENABLE_CARDINALITY_REDUCTION
    if cardinality_reduction_cnot_estimation < qubit_reduction_cnot_estimation:
        # if the state is sparse, we enable cardinality reduction method
        print_yellow("ENABLE_CARDINALITY_REDUCTION")
        ENABLE_QUBIT_REDUCTION = False
        ENABLE_CARDINALITY_REDUCTION = True
    else:
        print_yellow("ENABLE_QUBIT_REDUCTION")
        # otherwise, if the state is dense, we enable the qubit reduction method
        ENABLE_QUBIT_REDUCTION = True
        ENABLE_CARDINALITY_REDUCTION = False

    # initialize a circuit and the quantum registers
    circuit = QCircuit(state.num_qubits, map_gates=map_gates)

    with stopwatch("prepare_state") as timer:
        gates, _ = _prepare_state_rec(
            circuit,
            state,
            verbose_level=verbose_level,
            stats=stats,
        )

    if stats is not None:
        stats.time_total = timer.time()

    circuit.add_gates(gates)

    global_stopwatch_report()
    return circuit
