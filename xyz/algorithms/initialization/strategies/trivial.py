"""Cardinality-1 short-circuit — a computational-basis target only needs
X gates to swap in the right qubits, no rotations."""

from __future__ import annotations

from typing import List, Tuple

from xyz.algorithms.initialization.strategies.base import SynthesisStrategy
from xyz.algorithms.initialization.support_reduction import x_reduction


class TrivialStrategy(SynthesisStrategy):
    name = "trivial"

    def applicable(self, state, param) -> bool:
        return state.get_sparsity() == 1

    def synthesize(self, circuit, state):
        _, gates = x_reduction(circuit, state, False)
        return gates, 0
