#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-18 17:56:26
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 17:56:45
"""


class StatePreparationStatistics:
    """Classes the StatePreparationStatistics class ."""

    def __init__(self) -> None:
        self.time_total: float = 0
        self.num_runs_support_reduction: int = 0
        self.num_reduced_supports: int = 0
        self.num_reduced_density: int = 0
        self.num_saved_gates_decision: int = 0
        self.num_methods: dict = {}

        # time
        self.time_support_reduction: float = 0
        self.time_exact_cnot_synthesis: float = 0
        self.time_cardinality_reduction: float = 0
        self.time_qubit_decomposition: float = 0

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
