"""Qubit-reduction strategy (n-flow).

Reduces the qubit count by one via qubit_reduction, then recurses."""

from __future__ import annotations

from xyz.synthesis.n_flow import qubit_reduction
from xyz.synthesis.strategies.base import SynthesisStrategy
from xyz.utils import stopwatch


class NFlowStrategy(SynthesisStrategy):
    name = "qubit_reduction"

    def applicable(self, state, param) -> bool:
        return param.enable_n_flow

    def synthesize(self, circuit, state):
        supports = state.get_supports()
        with stopwatch("qubit_reduction") as timer:
            decomp_gates, new_state = qubit_reduction(circuit, state, supports)
        self.engine.stats.time_qubit_decomposition += timer.time()
        reduction_cnot = sum(g.cnot_cost() for g in decomp_gates)

        rec_gates, rec_cnot = self.engine.run(circuit, new_state)
        return rec_gates + decomp_gates, rec_cnot + reduction_cnot
