"""Cardinality-reduction strategy (m-flow).

Reduces the state's cardinality by one via cardinality_reduction, then
recurses on the smaller state through the engine."""

from __future__ import annotations

from xyz.synthesis.sparse_state_synthesis import (
    cardinality_reduction,
)
from xyz.synthesis.strategies.base import SynthesisStrategy
from xyz.utils import stopwatch


class MFlowStrategy(SynthesisStrategy):
    name = "sparse_qsp"

    def applicable(self, state, param) -> bool:
        return param.enable_m_flow

    def synthesize(self, circuit, state):
        with stopwatch("cardinality_reduction") as timer:
            new_state, reducing_gates = cardinality_reduction(
                circuit, state, verbose_level=self.engine.verbose_level
            )
        self.engine.stats.time_cardinality_reduction += timer.time()
        reduction_cnot = sum(g.cnot_cost() for g in reducing_gates)

        rec_gates, rec_cnot = self.engine.run(circuit, new_state)
        return rec_gates + reducing_gates, rec_cnot + reduction_cnot
