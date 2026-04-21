"""The Gate ABC: every concrete quantum gate honors this contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from xyz.gates.types import QBit, QGateType

if TYPE_CHECKING:
    from xyz.state.qstate import QState


class Gate(ABC):
    """Abstract base for all quantum gates.

    Every concrete gate must implement `apply`, `cnot_cost`, and
    `qubits`. `conjugate` is not abstract — gates that have a natural
    inverse override it; callers who invoke it on a gate without an
    override get a clear error.
    """

    qgate_type: QGateType

    def __init__(self, qgate_type: QGateType) -> None:
        self.qgate_type = qgate_type

    def __str__(self) -> str:
        return self.qgate_type.name

    @abstractmethod
    def apply(self, state: "QState") -> "QState":
        """Apply this gate to `state` and return the resulting state.
        Must be pure: do not mutate `state`."""

    @abstractmethod
    def cnot_cost(self) -> int:
        """Upper-bound CNOT count after mapping to {U2, CX}. Gates that
        contribute no CNOTs return 0."""

    @abstractmethod
    def qubits(self) -> List[QBit]:
        """All qubits this gate touches. Order: controls first (by
        ascending index), then targets."""

    def conjugate(self) -> "Gate":
        raise NotImplementedError(
            f"{type(self).__name__} does not define conjugate()"
        )


from xyz.gates.types import QBit  # noqa: E402


class BasicGate(Gate):
    """Common base for gates that act on a single target qubit.

    Still abstract — concrete subclasses must provide `apply`,
    `cnot_cost`, `qubits`."""

    def __init__(self, qgate_type, target_qubit: QBit) -> None:
        Gate.__init__(self, qgate_type)
        if not isinstance(target_qubit, QBit):
            raise TypeError(f"target_qubit {target_qubit!r} is not a QBit")
        self.target_qubit: QBit = target_qubit


class AdvancedGate(Gate):
    """Base for gates without a single canonical target qubit (e.g. MCMY).

    Subclasses provide `apply`, `cnot_cost`, `qubits` themselves."""


class MultiRotationGate:
    """Container for a list of rotation angles. Not a Gate — no apply/
    cnot_cost/qubits. Kept for backwards compat; appears unused by the
    regression suite but may be touched by external scripts."""

    def __init__(self, thetas) -> None:
        self.thetas = list(thetas)
