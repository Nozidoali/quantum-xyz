"""Quantum state preparation synthesis."""

from xyz.synthesis.prepare_state import prepare_state
from xyz.synthesis.params import StatePreparationParameters, Stats
from xyz.synthesis.deterministic_dicke_state import (
    TriState,
    SCSManager,
    prepare_dicke_state,
)
from xyz.synthesis.exact_cnot_synthesis import (
    QSPDatabase,
    AStarCost,
    Explorer,
    get_state_transitions,
    backtrace,
    exact_cnot_synthesis,
)
from xyz.synthesis.n_flow import (
    to_controlled_gate,
    select_pivot_qubit,
    select_informative_qubit,
    qubit_decomposition,
    qubit_reduction,
)
from xyz.synthesis.sparse_state_synthesis import (
    cardinality_reduction,
    depth_optimized_cardinality_reduction,
    sparse_state_synthesis,
    parallel_sparse_state_synthesis,
)

__all__ = [
    "prepare_state",
    "StatePreparationParameters",
    "Stats",
    # deterministic_dicke_state
    "TriState",
    "SCSManager",
    "prepare_dicke_state",
    # exact_cnot_synthesis
    "QSPDatabase",
    "AStarCost",
    "Explorer",
    "get_state_transitions",
    "backtrace",
    "exact_cnot_synthesis",
    # n_flow
    "to_controlled_gate",
    "select_pivot_qubit",
    "select_informative_qubit",
    "qubit_decomposition",
    "qubit_reduction",
    # sparse_state_synthesis
    "cardinality_reduction",
    "depth_optimized_cardinality_reduction",
    "sparse_state_synthesis",
    "parallel_sparse_state_synthesis",
]
