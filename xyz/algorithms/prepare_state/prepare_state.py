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


from xyz.circuit import QCircuit, QGate
from xyz.circuit import QState, quantize_state
from xyz.utils import stopwatch
from xyz.utils import global_stopwatch_report
from xyz.utils import print_yellow

from .exact_cnot_synthesis import exact_cnot_synthesis
from .m_flow import cardinality_reduction
from .n_flow import qubit_reduction
from .support_reduction import support_reduction, x_reduction
from ._stats import StatePreparationStatistics as Stats
from ._params import StatePreparationParameters as Params
from ._reindex import reindex_circuit


def _prepare_state_rec(
    circuit: QCircuit,
    state: QState,
    verbose_level: int = 0,
    param: Params = Params(),
    stats: Stats = Stats(),
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

    if param.enable_reindex:
        state, circuit = reindex_circuit(circuit, state)

    # get the states
    supports = state.get_supports()
    num_supports = len(supports)
    cardinality = state.get_sparsity()

    if verbose_level >= 3:
        print(f"state: {state}")

    stats.num_runs_support_reduction += 1
    stats.time_support_reduction += timer.time()
    stats.num_reduced_supports += prev_num_supports - num_supports
    stats.num_reduced_density += prev_density - cardinality

    # check for the trivial case
    if cardinality == 1:
        _, ground_state_calibration_gates = x_reduction(circuit, state, False)
        gates = ground_state_calibration_gates + support_reducing_gates
        # ground state calibration has 0 CNOT
        return gates, num_cx_support_reduction

    # exact synthesis
    if (
        param.enable_exact_synthesis
        and num_supports <= Params.EXACT_SYNTHESIS_QUBIT_THRESHOLD
        and cardinality <= Params.EXACT_SYNTHESIS_DENSITY_THRESHOLD
    ):
        print_yellow("EXACT SYNTHESIS")
        try:
            exact_gates = exact_cnot_synthesis(
                circuit,
                state,
                verbose_level=verbose_level,
                cnot_limit=Params.EXACT_SYNTHESIS_CNOT_LIMIT,
            )
            if stats is not None:
                stats.time_exact_cnot_synthesis += timer.time()
            gates = exact_gates + support_reducing_gates
            num_cx_exact = sum((gate.get_cnot_cost() for gate in exact_gates))
            return gates, num_cx_exact
        except ValueError:
            # if the exact synthesis fails
            pass

    # cardinality reduction method (m-flow)
    m_flow_gates: List[QGate] = None
    num_sparse_qsp_cx: int = 0
    if param.enable_m_flow:
        new_state, cardinality_reduction_gates = cardinality_reduction(
            circuit, state, verbose_level=verbose_level
        )
        num_cardinality_reduction_cx = sum(
            (gate.get_cnot_cost() for gate in cardinality_reduction_gates)
        )
        stats.time_cardinality_reduction += timer.time()
        rec_gates, rec_cx = _prepare_state_rec(
            circuit,
            new_state,
            stats=stats,
            param=param,
            verbose_level=verbose_level,
        )
        m_flow_gates = rec_gates + cardinality_reduction_gates + support_reducing_gates
        num_sparse_qsp_cx = (
            rec_cx + num_cardinality_reduction_cx + num_cx_support_reduction
        )

    # qubit reduction method (n-flow)
    n_flow_gates: List[QGate] = None
    num_qubit_reduction_cx: int = 0
    if param.enable_n_flow:
        qubit_decomposition_gates, new_state = qubit_reduction(circuit, state, supports)
        num_qubit_reduction_cx = sum(
            (gate.get_cnot_cost() for gate in qubit_decomposition_gates)
        )
        stats.time_qubit_decomposition += timer.time()
        rec_gates, rec_cx = _prepare_state_rec(
            circuit,
            new_state,
            stats=stats,
            param=param,
            verbose_level=verbose_level,
        )
        n_flow_gates = rec_gates + qubit_decomposition_gates + support_reducing_gates
        num_qubit_reduction_cx += rec_cx + num_cx_support_reduction

    # we choose the best one
    # based on the number of CNOT gates
    Method = namedtuple("method", ["name", "gates", "num_gates"])
    candidates = []

    if m_flow_gates is not None:
        candidates.append(Method("sparse_qsp", m_flow_gates, num_sparse_qsp_cx))
    if n_flow_gates is not None:
        candidates.append(
            Method("qubit_reduction", n_flow_gates, num_qubit_reduction_cx)
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
    param: Params = None,
    stats: Stats = Stats(),
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

    if param is None:
        # we design the default parameters
        param = Params()
        if cardinality_reduction_cnot_estimation < qubit_reduction_cnot_estimation:
            # if the state is sparse, we enable cardinality reduction method
            print_yellow("enable_m_flow")
            param.enable_n_flow = False
            param.enable_m_flow = True
        else:
            print_yellow("enable_n_flow")
            # otherwise, if the state is dense, we enable the qubit reduction method
            param.enable_n_flow = True
            param.enable_m_flow = False

    # initialize a circuit and the quantum registers
    circuit = QCircuit(state.num_qubits, map_gates=map_gates)

    with stopwatch("prepare_state") as timer:
        gates, _ = _prepare_state_rec(
            circuit,
            state,
            verbose_level=verbose_level,
            param=param,
            stats=stats,
        )

    if stats is not None:
        stats.time_total = timer.time()

    circuit.add_gates(gates)

    if verbose_level >= 1:
        global_stopwatch_report()
    return circuit
