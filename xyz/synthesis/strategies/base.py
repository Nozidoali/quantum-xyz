"""SynthesisStrategy ABC.

Each strategy knows how to synthesize a target QState into a list of
gates and reports its CNOT cost. Strategies hold a back-reference to
the engine so they can recurse on sub-states."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from xyz.circuit import QCircuit
    from xyz.state.qstate import QState
    from xyz.gates.base import Gate
    from xyz.synthesis.engine import SynthesisEngine
    from xyz.synthesis.params import (
        StatePreparationParameters,
    )


class SynthesisStrategy(ABC):
    """Abstract strategy that produces (gates, cnot_count) from a state."""

    name: str

    def __init__(self, engine: "SynthesisEngine") -> None:
        self.engine = engine

    @abstractmethod
    def applicable(
        self, state: "QState", param: "StatePreparationParameters"
    ) -> bool:
        """Cheap predicate: can this strategy handle the state at all?"""

    @abstractmethod
    def synthesize(
        self, circuit: "QCircuit", state: "QState"
    ) -> Tuple[List["Gate"], int]:
        """Return (gates, cnot_count). May call self.engine.run for
        recursive sub-problems (m-flow / n-flow do this; trivial / exact
        do not)."""
