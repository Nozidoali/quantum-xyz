#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-18 17:56:20
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 17:57:10
"""


class StatePreparationParameters:
    EXACT_SYNTHESIS_DENSITY_THRESHOLD = 100
    EXACT_SYNTHESIS_CNOT_LIMIT = 100

    def __init__(
        self,
        enable_exact_synthesis: bool = True,
        enable_n_flow: bool = False,
        enable_m_flow: bool = True,
        enable_decomposition: bool = False,
        enable_compression: bool = True,
        enable_reindex: bool = False,
        n_qubits_max: int = 4,
    ) -> None:
        self.enable_exact_synthesis: bool = enable_exact_synthesis
        self.enable_n_flow: bool = enable_n_flow
        self.enable_m_flow: bool = enable_m_flow
        self.enable_decomposition: bool = enable_decomposition
        self.enable_compression: bool = enable_compression
        self.enable_reindex: bool = enable_reindex
        self.n_qubits_max: int = n_qubits_max
