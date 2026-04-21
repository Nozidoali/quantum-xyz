"""The synthesis engine: orchestrates support reduction, short-circuit
strategies (Trivial, ExactCNOT), and competing strategies (MFlow,
NFlow)."""

from __future__ import annotations

from typing import List, Optional, Tuple

from xyz.algorithms.initialization.params import (
    StatePreparationParameters,
    Stats,
)
from xyz.algorithms.initialization.strategies.base import SynthesisStrategy
from xyz.algorithms.initialization.strategies.exact_cnot import (
    ExactCNOTStrategy,
)
from xyz.algorithms.initialization.strategies.m_flow import MFlowStrategy
from xyz.algorithms.initialization.strategies.n_flow import NFlowStrategy
from xyz.algorithms.initialization.strategies.trivial import TrivialStrategy
from xyz.algorithms.initialization.support_reduction import support_reduction
from xyz.utils import stopwatch


class SynthesisEngine:
    def __init__(
        self,
        param: StatePreparationParameters,
        stats: Optional[Stats] = None,
        verbose_level: int = 0,
    ) -> None:
        self.param = param
        self.stats = stats if stats is not None else Stats()
        self.verbose_level = verbose_level

        # Instantiation order mirrors evaluation order.
        self.trivial = TrivialStrategy(self)
        self.exact = ExactCNOTStrategy(self)
        self.m_flow = MFlowStrategy(self)
        self.n_flow = NFlowStrategy(self)

    def run(self, circuit, state) -> Tuple[list, int]:
        """Full pipeline on one state: support reduction → short-circuit
        strategies → competing strategies (pick best)."""

        if self.param.enable_reindex:
            raise NotImplementedError(
                "enable_reindex is not implemented; leave the flag at its default."
            )

        # Phase 1: support reduction.
        reducing_gates: list = []
        reduction_cnot = 0
        if self.param.enable_compression:
            with stopwatch("support_reduction") as timer:
                state, reducing_gates = support_reduction(
                    circuit, state, enable_cnot=True
                )
            reduction_cnot = sum(g.cnot_cost() for g in reducing_gates)
            self.stats.time_support_reduction += timer.time()

        self.stats.num_runs_support_reduction += 1

        # Phase 2: short-circuit strategies.
        if self.trivial.applicable(state, self.param):
            gates, cnot = self.trivial.synthesize(circuit, state)
            return gates + reducing_gates, cnot + reduction_cnot

        if self.exact.applicable(state, self.param):
            try:
                gates, cnot = self.exact.synthesize(circuit, state)
                return gates + reducing_gates, cnot + reduction_cnot
            except ValueError:
                pass  # exact synthesis bailed; fall through

        # Phase 3: competing strategies.
        candidates: List[Tuple[str, list, int]] = []
        for strategy in (self.m_flow, self.n_flow):
            if strategy.applicable(state, self.param):
                gates, cnot = strategy.synthesize(circuit, state)
                candidates.append((strategy.name, gates, cnot))

        if not candidates:
            raise RuntimeError(
                "no synthesis strategy applied — did you disable m-flow, "
                "n-flow, and exact synthesis all at once?"
            )

        best = min(candidates, key=lambda c: c[2])
        if len(candidates) > 1:
            worst = max(candidates, key=lambda c: c[2])
            self.stats.num_saved_gates_decision += worst[2] - best[2]
        self.stats.num_methods[best[0]] = (
            self.stats.num_methods.get(best[0], 0) + 1
        )
        return best[1] + reducing_gates, best[2] + reduction_cnot
