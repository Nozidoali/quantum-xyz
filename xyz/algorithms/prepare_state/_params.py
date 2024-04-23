#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-18 17:56:20
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 17:57:10
"""


class StatePreparationParameters:
    EXACT_SYNTHESIS_QUBIT_THRESHOLD = 4
    EXACT_SYNTHESIS_DENSITY_THRESHOLD = 10
    EXACT_SYNTHESIS_CNOT_LIMIT = 10

    def __init__(
        self,
        enable_exact_synthesis: bool = True,
        enable_n_flow: bool = False,
        enable_m_flow: bool = True,
        enable_decomposition: bool = False,
        enable_progress_bar: bool = True,
        enable_reindex: bool = False,
    ) -> None:
        self.enable_exact_synthesis: bool = enable_exact_synthesis
        self.enable_n_flow: bool = enable_n_flow
        self.enable_m_flow: bool = enable_m_flow
        self.enable_decomposition: bool = enable_decomposition
        self.enable_progress_bar: bool = enable_progress_bar
        self.enable_reindex: bool = enable_reindex
