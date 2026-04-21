"""Parameters and per-run statistics for state preparation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class StatePreparationParameters:
    EXACT_SYNTHESIS_DENSITY_THRESHOLD: int = 100
    EXACT_SYNTHESIS_CNOT_LIMIT: int = 100
    enable_exact_synthesis: bool = True
    enable_n_flow: bool = False
    enable_m_flow: bool = True
    enable_decomposition: bool = False
    enable_compression: bool = True
    enable_reindex: bool = False
    n_qubits_max: int = 5

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Stats:
    """Per-run counters for a state-preparation call."""

    time_total: float = 0.0
    num_runs_support_reduction: int = 0
    num_reduced_supports: int = 0
    num_reduced_density: int = 0
    num_saved_gates_decision: int = 0
    num_methods: Optional[Dict[str, int]] = None

    time_support_reduction: float = 0.0
    time_exact_cnot_synthesis: float = 0.0
    time_cardinality_reduction: float = 0.0
    time_qubit_decomposition: float = 0.0

    def __post_init__(self):
        if self.num_methods is None:
            self.num_methods = {}

    def report(self) -> None:
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
