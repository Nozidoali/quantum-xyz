"""Exact CNOT synthesis — used when the target fits the threshold.
Wraps the existing `exact_cnot_synthesis` function."""

from __future__ import annotations

from xyz.synthesis.exact_cnot_synthesis import (
    exact_cnot_synthesis,
)
from xyz.synthesis.strategies.base import SynthesisStrategy
from xyz.utils import stopwatch


class ExactCNOTStrategy(SynthesisStrategy):
    name = "exact_cnot"

    def applicable(self, state, param) -> bool:
        if not param.enable_exact_synthesis:
            return False
        return (
            len(state.get_supports()) <= param.n_qubits_max
            and state.get_sparsity() <= param.EXACT_SYNTHESIS_DENSITY_THRESHOLD
        )

    def synthesize(self, circuit, state):
        # The underlying call may raise ValueError when the CNOT limit is
        # exceeded; we let the engine catch that and fall back to the
        # competing strategies.
        with stopwatch("exact_cnot_synthesis") as timer:
            gates = exact_cnot_synthesis(
                circuit,
                state,
                verbose_level=self.engine.verbose_level,
                cnot_limit=self.engine.param.EXACT_SYNTHESIS_CNOT_LIMIT,
            )
        self.engine.stats.time_exact_cnot_synthesis += timer.time()
        cnot = sum(g.cnot_cost() for g in gates)
        return gates, cnot
