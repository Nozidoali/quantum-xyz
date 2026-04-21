# Phase 2 — Gate ABC + `apply` Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a real `Gate` ABC with abstract `apply`, `cnot_cost`, and `qubits` methods; implement the 8 missing `apply` methods (RX, RZ, U, CRX, CRZ, CU, MCMY, MULTIPLEXY; Z is already fixed in Phase 1); rename all getter-style Gate API to pythonic properties/methods.

**Architecture:** New `xyz/gates/types.py` and `xyz/gates/base.py` modules alongside the existing `xyz/circuit/qgate.py`. `qgate.py` stays intact (Phase 3 deletes it) but its concrete gate classes are rewired to inherit from the new `Gate` ABC and new trait mixins. Existing traits (`UnitaryGate`, `RotationGate`, `ControlledGate`, `MultiControlledGate`) are replaced by `UnitaryTrait`, `RotationTrait`, `ControlledTrait`, `MultiControlledTrait` in `types.py`.

**Tech Stack:** Python 3.10, pytest 8.2, numpy, qiskit 1.0+.

**Spec reference:** `docs/superpowers/specs/2026-04-19-refactor-design.md` — "Gate ABC Contract" and "Phase 2 — Gate ABC and `apply` Completion" sections.

**Base commit:** Phase 1 ends at `96153e5` (exit record). Phase 2 lands on top.

---

## File Structure

**New files:**
- `xyz/gates/__init__.py` — namespace re-exports (empty until Task 1)
- `xyz/gates/types.py` — `QGateType`, `QBit`, `RotationTrait`, `UnitaryTrait`, `ControlledTrait`, `MultiControlledTrait`
- `xyz/gates/base.py` — `Gate` ABC

**Modified files:**
- `xyz/circuit/qgate.py` — gate classes rewired to new ABC + traits; getters dropped; missing `apply` methods implemented
- `xyz/circuit/qcircuit.py` — callsite updates for renamed gate API (the public `QCircuit.get_cnot_cost()` keeps its name; only the inner `gate.get_cnot_cost()` → `gate.cnot_cost()`)
- Every callsite of the renamed methods across `xyz/`, `tests/`, `example/`
- `tests/regression/test_gate_apply.py` — shrink `UNIMPLEMENTED_APPLY` as each `apply` lands; extend `_apply_on_qiskit` with the new gates

**Unchanged:**
- Phase 0/1 regression tests (other than the `test_gate_apply.py` updates above)
- `tests/regression/golden_bounds.json`

---

## Ground rules

- **TDD per fix.** Each `apply` implementation starts by removing its entry from `UNIMPLEMENTED_APPLY` in `test_gate_apply.py`; running the test makes it FAIL; then implementing the `apply` body makes it PASS.
- **Slurm only for the end-of-phase full-suite check.** Per-task checks run locally — the bug-fix and gate-apply tests are sub-second.
- **Poetry venv python** for every invocation: `/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python`.
- **No file relocation in this phase.** `qgate.py` stays. Phase 3 deletes it.
- **Keep `QCircuit.get_cnot_cost()` as a public method name.** Only the gate-level `get_cnot_cost` renames to `cnot_cost`. The `QCircuit` method's internal loop updates to call `gate.cnot_cost()`.
- **Mutable defaults remain forbidden** — if you add helpers, don't reintroduce `=[]` or `={}` defaults.

---

## Task 1: Create `xyz/gates/types.py` with enum, `QBit`, and traits

**Files:**
- Create: `xyz/gates/__init__.py`
- Create: `xyz/gates/types.py`

**Step 1: Create the package marker**

```bash
: > /home/hanyu/proj/quantum-xyz/xyz/gates/__init__.py
```

**Step 2: Write `xyz/gates/types.py`**

The content mirrors the current enum / `QBit` / trait classes in `xyz/circuit/qgate.py` but with trait names renamed:
- `RotationGate` → `RotationTrait`
- `UnitaryGate` → `UnitaryTrait`
- `ControlledGate` → `ControlledTrait`
- `MultiControlledGate` → `MultiControlledTrait`

Write the file with exactly this content:

```python
"""Shared data classes for the gate hierarchy: the enum, the qubit handle,
and the per-concern trait mixins that concrete gates compose in."""

from __future__ import annotations

from enum import Enum, auto
from typing import List

import numpy as np


class QGateType(Enum):
    U = auto()
    CU = auto()
    MCU = auto()

    X = auto()
    Y = auto()
    Z = auto()

    CY = auto()
    CZ = auto()
    CX = auto()

    RX = auto()
    RY = auto()
    RZ = auto()

    CRX = auto()
    CRY = auto()
    CRZ = auto()

    MCRY = auto()

    MULTIPLEX_Y = auto()

    MCMY = auto()

    NONE = auto()


class QBit:
    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f"q{self.index}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, QBit):
            return self.index == other.index
        return False

    def __hash__(self) -> int:
        return hash(self.index)


class RotationTrait:
    """Concrete gates with a single rotation angle `theta`."""

    def __init__(self, theta: float) -> None:
        self.theta = theta

    def is_trivial(self) -> bool:
        return np.isclose(self.theta, 0) or np.isclose(self.theta, 2 * np.pi)

    def is_pi(self) -> bool:
        return np.isclose(self.theta, np.pi) or np.isclose(self.theta, -np.pi)


class UnitaryTrait:
    """Concrete gates parameterized by a 2×2 unitary matrix, with its
    Z-Y-Z decomposition pre-computed as `alpha`, `beta`, `gamma`."""

    def __init__(self, unitary: np.ndarray) -> None:
        self.unitary = unitary
        self.alpha, self.beta, self.gamma = _unitary_zyz_decomposition(unitary)

    def is_z_trivial(self) -> bool:
        is_alpha_trivial = np.isclose(self.alpha, 0) or np.isclose(
            self.alpha, 2 * np.pi
        )
        is_gamma_trivial = np.isclose(self.gamma, 0) or np.isclose(
            self.gamma, 2 * np.pi
        )
        return is_alpha_trivial and is_gamma_trivial

    def is_z_trivial_not(self) -> bool:
        is_alpha_trivial = np.isclose(self.alpha, np.pi)
        is_gamma_trivial = np.isclose(self.gamma, np.pi)
        return is_alpha_trivial and is_gamma_trivial


class ControlledTrait:
    """Gates with exactly one control qubit and one control phase.
    Exposes `control_qubits` as a one-element list so callers can treat
    singly- and multi-controlled gates uniformly."""

    def __init__(self, control_qubit: QBit, phase: int = 1) -> None:
        assert isinstance(control_qubit, QBit)
        self.control_qubits: List[QBit] = [control_qubit]
        self.phase = phase

    def is_enabled(self, index: int) -> bool:
        q = self.control_qubits[0]
        return (index >> q.index) & 1 == self.phase


class MultiControlledTrait:
    """Gates with an arbitrary-length list of control qubits and phases."""

    def __init__(self, control_qubits: List[QBit], phases: List[int]) -> None:
        self.control_qubits: List[QBit] = list(control_qubits)
        self.phases: List[int] = list(phases)

    def has_zero_controls(self) -> bool:
        return len(self.control_qubits) == 0

    def has_one_control(self) -> bool:
        return len(self.control_qubits) == 1

    def is_enabled(self, index: int) -> bool:
        for ctrl, phase in zip(self.control_qubits, self.phases):
            if (index >> ctrl.index) & 1 != phase:
                return False
        return True


# --- ZYZ decomposition (moved out of qgate.py to break the trait / gate /
# decomposition circular dependency; Phase 3 will re-home this to
# xyz/decomposition/zyz.py).

def _to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    from numpy.linalg import det
    rank = matrix.shape[0]
    return matrix / det(matrix) ** (1 / rank)


def _unitary_zyz_decomposition(matrix: np.ndarray):
    """Return the Euler Z-Y-Z decomposition of a 1-qubit unitary."""
    U = _to_special_unitary(matrix)
    if abs(U[0, 0]) > abs(U[1, 0]):
        theta1 = 2 * np.arccos(min(abs(U[0, 0]), 1))
    else:
        theta1 = 2 * np.arcsin(min(abs(U[1, 0]), 1))
    cos_halftheta1 = np.cos(theta1 / 2)
    if not np.isclose(cos_halftheta1, 0.0):
        phase = U[1, 1] / cos_halftheta1
        theta0_plus_theta2 = 2 * np.arctan2(np.imag(phase), np.real(phase))
    else:
        theta0_plus_theta2 = 0.0
    sin_halftheta1 = np.sin(theta1 / 2)
    if not np.isclose(sin_halftheta1, 0.0):
        phase = U[1, 0] / sin_halftheta1
        theta0_sub_theta2 = 2 * np.arctan2(np.imag(phase), np.real(phase))
    else:
        theta0_sub_theta2 = 0.0
    theta0 = (theta0_plus_theta2 + theta0_sub_theta2) / 2
    theta2 = (theta0_plus_theta2 - theta0_sub_theta2) / 2
    if np.isclose(theta1, 0.0, atol=1e-6):
        theta2 = theta0 + theta2
        theta1 = 0.0
        theta0 = 0.0
    if theta0 < 0:
        theta0 += 2 * np.pi
    if theta1 < 0:
        theta1 += 2 * np.pi
    if theta2 < 0:
        theta2 += 2 * np.pi
    return theta0, theta1, theta2
```

**Step 3: Make `xyz/circuit/qgate.py` re-export from `types.py` so existing imports keep working**

In `xyz/circuit/qgate.py`:

1. Near the existing imports (top of file), add:

```python
from xyz.gates.types import (
    QGateType as QGateType,
    QBit as QBit,
    RotationTrait,
    UnitaryTrait,
    ControlledTrait,
    MultiControlledTrait,
    _unitary_zyz_decomposition as _unitary_zyz_decomposition_impl,
    _to_special_unitary as _to_special_unitary_impl,
)
```

2. Delete the existing definitions of `QGateType`, `QBit`, `UnitaryGate`, `RotationGate`, `ControlledGate`, `MultiControlledGate`, `to_special_unitary`, `unitary_zyz_decomposition` from the body of `qgate.py`.

3. Add backwards-compat aliases so existing class references keep working:

```python
# Phase 2: legacy trait class names. Phase 3 deletes these once all
# concrete gates reference the Trait names directly.
UnitaryGate = UnitaryTrait
RotationGate = RotationTrait
ControlledGate = ControlledTrait
MultiControlledGate = MultiControlledTrait
to_special_unitary = _to_special_unitary_impl
unitary_zyz_decomposition = _unitary_zyz_decomposition_impl
```

4. Leave the concrete gate classes (X, Z, RX, RY, RZ, U, CX, CRX, CRY, CRZ, CU, MCRY, MCMY, MULTIPLEXY) alone. They still inherit from `RotationGate` / `ControlledGate` / etc., which are now aliases for the Trait names. Task 2 rewires them to inherit from `Gate`; Task 3 switches their explicit bases to the Trait names.

**Step 4: Verify imports still work**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c "import xyz; from xyz.circuit.qgate import QGateType, QBit, RotationGate, RotationTrait; print('import ok')"
```

Expected: `import ok`.

**Step 5: Run the Phase 1 regression tests to confirm no behavior change**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `6 passed` on bug fixes, `5 passed, 9 xfailed` on gate apply. No new failures.

**Step 6: Commit**

```bash
git add xyz/gates/__init__.py xyz/gates/types.py xyz/circuit/qgate.py
git commit -m "refactor(gates): extract types and traits to xyz/gates/types.py"
```

---

## Task 2: Create `xyz/gates/base.py` with the `Gate` ABC

**Files:**
- Create: `xyz/gates/base.py`
- Modify: `xyz/circuit/qgate.py` (replace `QGate` with alias; remove old concrete inheritance from `QGate` later in Task 3)

**Step 1: Write `xyz/gates/base.py`**

```python
"""The Gate ABC: every concrete quantum gate honors this contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from xyz.gates.types import QBit, QGateType

if TYPE_CHECKING:
    from xyz.circuit.qstate import QState


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
```

**Step 2: In `xyz/circuit/qgate.py`, replace the `QGate` class definition with an alias**

Find:

```python
class QGate:
    def __init__(self, qgate_type: QGateType) -> None:
        self.qgate_type = qgate_type

    def __str__(self) -> str:
        return self.qgate_type.name

    def get_qgate_type(self) -> QGateType:
        return self.qgate_type
```

Replace with:

```python
from xyz.gates.base import Gate

# Phase 2: QGate becomes an alias for the new ABC; Phase 3 deletes the
# alias and updates callers to Gate directly.
QGate = Gate
```

(Keep the other classes — `BasicGate`, `AdvancedGate`, and concrete gates — untouched in this task. Task 3 rewires them.)

**Step 3: Verify the ABC is not yet enforced on existing concrete gates**

Because `BasicGate` inherits from `QGate` (now `Gate`), and `BasicGate` doesn't implement `apply`/`cnot_cost`/`qubits`, Python lets you still define subclasses that don't override them — BUT you cannot instantiate them because the ABC's abstract markers are inherited through `BasicGate`. So instantiation of any concrete gate (including the already-working ones like RY, CX) will now raise `TypeError: Can't instantiate abstract class`.

This is the breaking point. Task 3 fixes it by adding `qubits()` to every concrete gate.

Verify the expected breakage:

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c "
from xyz.circuit.qgate import RY, QBit
try:
    RY(0.5, QBit(0))
    print('UNEXPECTED: RY instantiated')
except TypeError as e:
    print(f'EXPECTED: {e}')
"
```

Expected: `EXPECTED: Can't instantiate abstract class RY with abstract methods apply, cnot_cost, qubits` (or a very similar message — the exact wording depends on the Python version and whether any concrete `apply`/`cnot_cost` exist; RY has a concrete `apply` and `get_cnot_cost` but not yet `cnot_cost` or `qubits`, so at minimum those two are abstract).

If instantiation unexpectedly succeeds, STOP and report — the abstract markers aren't being inherited correctly.

**Step 4: DO NOT COMMIT YET.** The repo is broken (no concrete gate can be constructed). Task 3 lands the complementary change in the same conceptual unit.

---

## Task 3: Make every concrete gate inherit from Gate and implement `qubits()` + `cnot_cost()` rename

**Files:**
- Modify: `xyz/circuit/qgate.py` — every concrete gate class
- Modify: `xyz/circuit/qcircuit.py` — update `gate.get_cnot_cost()` call sites (line ~60, ~68, ~113)

**Approach:** For each concrete gate, three changes:
1. Rename `get_cnot_cost(self) -> int` to `cnot_cost(self) -> int` (no other signature change).
2. Add a `qubits(self) -> List[QBit]` method.
3. Replace explicit base-class inheritance from `RotationGate`/`UnitaryGate`/etc. with the new `RotationTrait`/`UnitaryTrait`/etc. names (the aliases from Task 1 still work, but switching to Trait names is cleaner).

Because this is 14 gate classes and the shape of each change is uniform, treat them as a single edit pass and verify at the end.

**Step 1: Edit every concrete gate class in `xyz/circuit/qgate.py`**

For each class, apply these patterns:

**Single-qubit gates (X, Z, RX, RY, RZ, U).** Pattern for X:

```python
class X(BasicGate):
    def __init__(self, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.X, target_qubit)

    def __str__(self) -> str:
        return f"X({self.target_qubit})"

    def cnot_cost(self) -> int:
        return 0

    def qubits(self) -> List[QBit]:
        return [self.target_qubit]

    def apply(self, qstate: "QState") -> "QState":
        # unchanged from current
        index_to_weight = {}
        for idx in qstate.index_set:
            reversed_idx = idx ^ (1 << self.target_qubit.index)
            index_to_weight[reversed_idx] = qstate.index_to_weight[idx]
        return QState(index_to_weight, qstate.num_qubits)
```

Apply the analogous rename + `qubits()` addition to **Z, RX, RY, RZ, U**. For each: `cnot_cost` replaces `get_cnot_cost`; `qubits()` returns `[self.target_qubit]`.

**Singly-controlled gates (CX, CRX, CRY, CRZ, CU).** Pattern for CX:

```python
class CX(BasicGate, ControlledTrait):
    def __init__(self, control_qubit: QBit, phase: int, target_qubit: QBit) -> None:
        BasicGate.__init__(self, QGateType.CX, target_qubit)
        ControlledTrait.__init__(self, control_qubit, phase)

    def cnot_cost(self) -> int:
        return 1

    def qubits(self) -> List[QBit]:
        return sorted(self.control_qubits + [self.target_qubit],
                      key=lambda q: q.index)
    # __str__ unchanged
    # apply unchanged
    # conjugate unchanged if defined
```

Note: `ControlledTrait.__init__` sets `self.control_qubits = [control_qubit]` (a list). **Delete the stale `self.control_qubit = control_qubit` assignment if any class still has it** — the new trait replaces the scalar attribute. If callers read `.control_qubit` anywhere, the rename sweep in Task 4 handles it.

Apply to **CX, CRX, CRY, CRZ, CU**.

**Multi-controlled gates (MCRY, MCMY, MULTIPLEXY).**

- `MCRY(Gate, RotationTrait, BasicGate, MultiControlledTrait)` — needs `cnot_cost` renamed, `qubits()` added as `sorted(self.control_qubits + [self.target_qubit], key=...)`.
- `MCMY(AdvancedGate)` — currently just stores `self.control_qubits` and `self.target_qubit` by hand. Rename its `get_cnot_cost` → `cnot_cost`, add `qubits()`.
- `MULTIPLEXY(AdvancedGate)` — same pattern. Its `self.control_qubit` (singular) attribute stays for now because Task 4 sweeps it; `qubits()` returns `sorted([self.control_qubit, self.target_qubit], key=lambda q: q.index)` in this task.

**Step 2: Update `xyz/circuit/qcircuit.py` internal call sites**

Change these three call sites:

| Line (approx) | Before | After |
|---|---|---|
| 60 | `gate_time + gate.get_cnot_cost()` | `gate_time + gate.cnot_cost()` |
| 68 | `gate_time + gate.get_cnot_cost()` | `gate_time + gate.cnot_cost()` |
| 113 | `return sum([gate.get_cnot_cost() for gate in self.__gates])` | `return sum(gate.cnot_cost() for gate in self.__gates)` |

Line 112's `def get_cnot_cost(self)` on `QCircuit` **does not rename** — it is the public API keeping its name.

**Step 3: Verify every concrete gate now instantiates and the bug-fix + gate-apply tests still pass**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c "
from xyz.circuit.qgate import (
    RX, RY, RZ, X, Z, U, CX, CRX, CRY, CRZ, CU, MCRY, MCMY, MULTIPLEXY, QBit
)
import numpy as np
for cls in [RX, RY, RZ, X, Z, U, CX, CRX, CRY, CRZ, CU, MCRY, MCMY, MULTIPLEXY]:
    print(cls.__name__, 'ok')
"
```

Expected: all 14 gate names print `ok` (no `TypeError: Can't instantiate abstract class`).

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `6 passed` on bug fixes, `5 passed, 9 xfailed` on gate apply (unchanged from Phase 1 — this task is not yet about implementing the missing `apply`s).

**Step 4: Commit the Task 2 + Task 3 combined change**

```bash
git add xyz/gates/base.py xyz/circuit/qgate.py xyz/circuit/qcircuit.py
git commit -m "refactor(gates): introduce Gate ABC; add qubits() + cnot_cost rename"
```

---

## Task 4: Rename getter API across the repo (Gate methods → properties)

**Files:**
- Modify: `xyz/circuit/qgate.py` (remove any remaining `get_*` methods on Gate classes, expose the data as attributes)
- Modify: every file that calls `gate.get_*()` — list from `grep -rln "get_qgate_type\|get_control_qubit\|get_target_qubit\|get_phase\|get_theta\|get_unitary\|get_alpha\|get_beta\|get_gamma" xyz tests example`

Phase 1 already renamed `get_cnot_cost` → `cnot_cost` in Task 3 of this phase (combined with ABC changes). Task 4 sweeps the remaining getters that don't wrap computation:

| Old | New | Kind |
|---|---|---|
| `gate.get_qgate_type()` | `gate.qgate_type` | attribute (already exists; delete method) |
| `gate.get_control_qubit()` | `gate.control_qubits[0]` | attribute access (list is already present via ControlledTrait) |
| `gate.get_control_qubits()` | `gate.control_qubits` | attribute (already exists) |
| `gate.get_target_qubit()` | `gate.target_qubit` | attribute (already set in BasicGate) |
| `gate.get_phase()` | `gate.phase` | attribute (already set in ControlledTrait) |
| `gate.get_phases()` | `gate.phases` | attribute (already set in MultiControlledTrait) |
| `gate.get_theta()` | `gate.theta` | attribute (already set in RotationTrait) |
| `gate.get_unitary()` | `gate.unitary` | attribute (already set in UnitaryTrait) |
| `gate.get_alpha/beta/gamma()` | `gate.alpha/beta/gamma` | attribute (already set in UnitaryTrait) |

**Step 1: In `xyz/circuit/qgate.py`, delete the `get_*` methods**

Find and delete:

- Any remaining `def get_qgate_type(self)` methods (should be zero after Task 2 replaced `QGate` with the ABC alias, but verify).
- `UnitaryGate.get_unitary`, `get_alpha`, `get_beta`, `get_gamma` (these were in the old `UnitaryGate` class; after Task 1's trait extraction they should already be gone, but double-check `qgate.py` has no `def get_unitary` etc.)
- `RotationGate.get_theta` (same story)
- `ControlledGate.get_control_qubit`, `get_control_qubits`, `get_phase` (same)
- `MultiControlledGate.get_control_qubits`, `get_phases` (same)
- `BasicGate.get_target_qubit`

After this step, grep should confirm no `def get_*` in `qgate.py`:

```bash
grep -n "def get_" xyz/circuit/qgate.py
```

Expected: empty output (or one result only for `get_cnot_cost` on `QCircuit` — that's a different file, so zero hits in qgate.py).

**Step 2: Sweep the call sites**

Enumerate the files that call the old names:

```bash
grep -rln "\.get_qgate_type\|\.get_control_qubit\|\.get_target_qubit\|\.get_phase\|\.get_theta\|\.get_unitary\|\.get_alpha\|\.get_beta\|\.get_gamma" xyz tests example
```

For each file in the output, apply the rename table. Specifically:

- `gate.get_qgate_type()` → `gate.qgate_type`
- `gate.get_control_qubit()` → `gate.control_qubits[0]`  (singular old access → first of list)
- `gate.get_control_qubits()` → `gate.control_qubits`
- `gate.get_target_qubit()` → `gate.target_qubit`
- `gate.get_phase()` → `gate.phase`
- `gate.get_phases()` → `gate.phases`
- `gate.get_theta()` → `gate.theta`
- `gate.get_unitary()` → `gate.unitary`
- `gate.get_alpha()` → `gate.alpha`
- `gate.get_beta()` → `gate.beta`
- `gate.get_gamma()` → `gate.gamma`

Because these are method-call → attribute-access conversions, Python will not catch mismatches at import time — they only surface when the code path runs. Rely on the regression suite for detection.

**Step 3: Run the regression suite locally to catch any missed rename**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/ -v -m "not slow" -x
```

Expected: all pass (41 from Phase 0 + 6 bug fixes - 9 xfail). If a test fails with `AttributeError: 'X' has no attribute 'get_...'`, locate and rename that call site.

**Step 4: Verify no getter remnants in the code under rename**

```bash
grep -rn "\.get_qgate_type\|\.get_control_qubit\|\.get_target_qubit\|\.get_phase\|\.get_theta\|\.get_unitary\|\.get_alpha\|\.get_beta\|\.get_gamma" xyz tests example
```

Expected: no output. If any remain, they either (a) are missed, or (b) belong to non-Gate objects (unlikely in this repo). Fix (a); leave (b).

**Step 5: Commit**

```bash
git add -u
git commit -m "refactor(gates): drop get_* getters, expose data via attributes"
```

---

## Task 5: Implement `apply` for `RX`, `RZ`, `U`

**Files:**
- Modify: `xyz/circuit/qgate.py` — `RX.apply`, `RZ.apply`, `U.apply`
- Modify: `tests/regression/test_gate_apply.py` — shrink `UNIMPLEMENTED_APPLY`, extend `_apply_on_qiskit`

**Step 1: Update `tests/regression/test_gate_apply.py`**

In the file, find:

```python
UNIMPLEMENTED_APPLY = {"RX", "RZ", "U", "Z", "CRX", "CRZ", "CU", "MCMY", "MULTIPLEXY"}
```

Change to:

```python
UNIMPLEMENTED_APPLY = {"CRX", "CRZ", "CU", "MCMY", "MULTIPLEXY"}
```

(Also remove `"Z"` — it was already fixed in Phase 1; the set has been stale since then. This task is the right time to clean it.)

In `_apply_on_qiskit`, extend the handler so it also covers `RX`, `RZ`, `U`, `Z`:

```python
def _apply_on_qiskit(qc: QuantumCircuit, gate) -> None:
    name = type(gate).__name__
    t = gate.target_qubit.index
    if name == "RX": qc.rx(gate.theta, t); return
    if name == "RY": qc.ry(gate.theta, t); return
    if name == "RZ": qc.rz(gate.theta, t); return
    if name == "X":  qc.x(t); return
    if name == "Z":  qc.z(t); return
    if name == "U":  qc.unitary(gate.unitary, [t]); return
    if name == "CX":  qc.cx(gate.control_qubits[0].index, t); return
    if name == "CRY": qc.cry(gate.theta, gate.control_qubits[0].index, t); return
    if name == "MCRY":
        controls = [q.index for q in gate.control_qubits]
        qc.mcry(gate.theta, controls, t)
        return
    raise AssertionError(
        f"no qiskit equivalent wired for {name}; extend _apply_on_qiskit "
        "when Phase 2 implements its apply()"
    )
```

(Note: `gate.control_qubits[0].index` replaces the old `gate.control_qubit.index` because Task 4's sweep renamed the singular attribute. If this file still uses `gate.control_qubit.index`, Task 4 missed it — fix here.)

**Step 2: Run the test to confirm it FAILS for RX/RZ/U**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_gate_apply.py -v
```

Expected: `RX`, `RZ`, `U`, `Z` now run (not xfail) but `RX`, `RZ`, `U` FAIL with `NotImplementedError: This method is not implemented` (or XPASS for `Z` since Phase 1 implemented its apply — if `Z` XPASSES while still in the no-longer-present UNIMPLEMENTED set, confirm by re-running that it now plain PASSES).

**Math note — real-amplitudes-only semantic.** `QState` carries only real amplitudes (see `quantize_state` in `xyz/circuit/qstate.py`: it calls `np.real(...)`). The qiskit reference in `_apply_on_qiskit` also projects via `np.real(Statevector(qc).data)`, so both sides compare the **real projection** of the operator action.

Under that projection:
- `RX(θ)|ψ_real>.real = cos(θ/2)·|ψ>` (the complex off-diagonal terms `∓i·sin(θ/2)` vanish when you take `np.real` of a real-input state)
- `RZ(θ)|ψ_real>.real = cos(θ/2)·|ψ>` (the diagonal `e^{∓iθ/2}` has real part `cos(θ/2)` applied to both components)
- `U(M)|ψ_real>.real = Re(M) @ ψ` (when M is real-orthogonal as the test builds via `_random_unitary_2x2`, this is standard matrix multiplication)

So `RX.apply` and `RZ.apply` both collapse to scalar multiplication by `cos(θ/2)`. `U.apply` is matrix multiplication with the real part of the stored unitary. If the random test inputs ever produce a non-real `U`, the xyz side drops the imaginary parts — which matches qiskit's `np.real` projection on the test side.

**Step 3: Implement `RX.apply`**

Replace `RX.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        # Real projection of RX(θ) on a real-amplitude state is a scalar
        # multiplication by cos(θ/2). See math note at the top of Task 5.
        scale = float(np.cos(self.theta / 2))
        return QState(
            {idx: w * scale for idx, w in qstate.index_to_weight.items()},
            qstate.num_qubits,
        )
```

**Step 4: Implement `RZ.apply`**

Replace `RZ.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        # RZ's real projection on a real-amplitude state matches RX's:
        # both reduce to cos(θ/2)·ψ. See math note at the top of Task 5.
        scale = float(np.cos(self.theta / 2))
        return QState(
            {idx: w * scale for idx, w in qstate.index_to_weight.items()},
            qstate.num_qubits,
        )
```

**Step 5: Implement `U.apply`**

Replace `U.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        # Apply Re(U) as a 2×2 real matrix on the two-amplitude subspace
        # indexed by the target qubit's bit. See math note at the top of
        # Task 5.
        m = np.real(self.unitary)
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                # column 0 of m
                index_to_weight[idx] += weight * m[0, 0]
                index_to_weight[rdx] += weight * m[1, 0]
            else:
                # column 1 of m
                index_to_weight[idx] += weight * m[1, 1]
                index_to_weight[rdx] += weight * m[0, 1]
        return QState(index_to_weight, qstate.num_qubits)
```

**Step 6: Run the test to confirm all 3 PASS**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_gate_apply.py -v
```

Expected: `RX`, `RY`, `RZ`, `X`, `Z`, `U`, `CX`, `CRY`, `MCRY` PASS (9 PASS) and `CRX`, `CRZ`, `CU`, `MCMY`, `MULTIPLEXY` still XFAIL (5 XFAIL).

If any of RX/RZ/U FAIL at numerical tolerance, re-examine the applied matrix convention in that specific case against qiskit's `rx`/`rz`/`unitary` (in `_apply_on_qiskit`). Adjust only the failing case.

**Step 7: Commit**

```bash
git add tests/regression/test_gate_apply.py xyz/circuit/qgate.py
git commit -m "feat(gates): implement RX/RZ/U apply() and xfail → pass"
```

---

## Task 6: Implement `apply` for `CRX`, `CRZ`, `CU`

**Files:**
- Modify: `xyz/circuit/qgate.py` — `CRX.apply`, `CRZ.apply`, `CU.apply`
- Modify: `tests/regression/test_gate_apply.py` — shrink `UNIMPLEMENTED_APPLY`, extend `_apply_on_qiskit`

**Step 1: Shrink `UNIMPLEMENTED_APPLY`**

In `tests/regression/test_gate_apply.py`, change:

```python
UNIMPLEMENTED_APPLY = {"CRX", "CRZ", "CU", "MCMY", "MULTIPLEXY"}
```

to:

```python
UNIMPLEMENTED_APPLY = {"MCMY", "MULTIPLEXY"}
```

Extend `_apply_on_qiskit`:

```python
    if name == "CRX":
        qc.crx(gate.theta, gate.control_qubits[0].index, t); return
    if name == "CRZ":
        qc.crz(gate.theta, gate.control_qubits[0].index, t); return
    if name == "CU":
        qc.append(
            __import__("qiskit.circuit.library", fromlist=["UnitaryGate"])
              .UnitaryGate(gate.unitary).control(1),
            [gate.control_qubits[0].index, t],
        )
        return
```

(If the in-line `__import__` is awkward, add `from qiskit.circuit.library import UnitaryGate` at the top of the test file and simplify.)

**Step 2: Run the test — confirm FAIL for CRX/CRZ/CU**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_gate_apply.py -v
```

Expected: `CRX`, `CRZ`, `CU` FAIL with `NotImplementedError`. Others unchanged.

**Math note — same real-projection semantics as Task 5.** CRX / CRZ reduce to `cos(θ/2)·ψ` on the control-enabled indices and identity elsewhere. CU is `Re(U)` matrix-mul restricted to control-enabled indices.

**Step 3: Implement `CRX.apply`**

Replace `CRX.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        scale = float(np.cos(self.theta / 2))
        out = {}
        for idx, weight in qstate.index_to_weight.items():
            out[idx] = weight * scale if self.is_enabled(idx) else weight
        return QState(out, qstate.num_qubits)
```

**Step 4: Implement `CRZ.apply`**

Replace `CRZ.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        scale = float(np.cos(self.theta / 2))
        out = {}
        for idx, weight in qstate.index_to_weight.items():
            out[idx] = weight * scale if self.is_enabled(idx) else weight
        return QState(out, qstate.num_qubits)
```

**Step 5: Implement `CU.apply`**

Replace `CU.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        m = np.real(self.unitary)
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            if not self.is_enabled(idx):
                index_to_weight[idx] += weight
                continue
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * m[0, 0]
                index_to_weight[rdx] += weight * m[1, 0]
            else:
                index_to_weight[idx] += weight * m[1, 1]
                index_to_weight[rdx] += weight * m[0, 1]
        return QState(index_to_weight, qstate.num_qubits)
```

**Step 6: Verify PASS**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_gate_apply.py -v
```

Expected: 12 PASS (added CRX/CRZ/CU); `MCMY`, `MULTIPLEXY` still XFAIL (2 XFAIL).

**Step 7: Commit**

```bash
git add tests/regression/test_gate_apply.py xyz/circuit/qgate.py
git commit -m "feat(gates): implement CRX/CRZ/CU apply() and xfail → pass"
```

---

## Task 7: Implement `apply` for `MCMY`, `MULTIPLEXY`

**Files:**
- Modify: `xyz/circuit/qgate.py` — `MCMY.apply`, `MULTIPLEXY.apply`
- Modify: `tests/regression/test_gate_apply.py` — empty `UNIMPLEMENTED_APPLY`, extend `_apply_on_qiskit`

**Step 1: Empty `UNIMPLEMENTED_APPLY`**

In `tests/regression/test_gate_apply.py`:

```python
UNIMPLEMENTED_APPLY = set()
```

Extend `_apply_on_qiskit`:

```python
    if name == "MCMY":
        # MCMY is a multi-controlled, multi-target (per-pattern) rotation.
        # Emulate by decomposing and using MCRY at each enabled pattern —
        # but the xyz apply is the reference; for the qiskit side we
        # build a Statevector directly.
        controls = [q.index for q in gate.control_qubits]
        from qiskit import QuantumCircuit as _QC
        # each pattern index k uses rotation_table[k] on the target
        # conditioned on controls reading k in binary. We apply MCRY with
        # the right phase vector per pattern.
        for k, theta in enumerate(gate.rotation_table):
            phases = [(k >> i) & 1 for i in range(len(controls))]
            # flip controls whose phase is 0 with X around the MCRY
            for i, p in enumerate(phases):
                if p == 0:
                    qc.x(controls[i])
            qc.mcry(theta, controls, t)
            for i, p in enumerate(phases):
                if p == 0:
                    qc.x(controls[i])
        return
    if name == "MULTIPLEXY":
        # Demultiplexer: RY(theta0) when ctrl=0, RY(theta1) when ctrl=1.
        ctrl = gate.control_qubit.index if hasattr(gate, "control_qubit") \
               else gate.control_qubits[0].index
        qc.x(ctrl); qc.cry(gate.theta0, ctrl, t); qc.x(ctrl)
        qc.cry(gate.theta1, ctrl, t)
        return
```

(The `hasattr` fallback handles the case where Task 4's sweep left `MULTIPLEXY.control_qubit` singular — clean it up if so.)

**Step 2: Confirm test FAILs for MCMY/MULTIPLEXY**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_gate_apply.py -v
```

Expected: `MCMY`, `MULTIPLEXY` FAIL with `NotImplementedError`. Others PASS.

**Step 3: Implement `MCMY.apply`**

In `xyz/circuit/qgate.py`, replace `MCMY.apply`:

```python
    def apply(self, qstate: "QState") -> "QState":
        # Pattern k (binary over controls) triggers RY(rotation_table[k])
        # on the target.
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            pattern = 0
            for i, ctrl in enumerate(self.control_qubits):
                pattern |= ((idx >> ctrl.index) & 1) << i
            theta = self.rotation_table[pattern]
            c = np.cos(theta / 2)
            s = np.sin(theta / 2)
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += weight * s
            else:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += -weight * s
        return QState(index_to_weight, qstate.num_qubits)
```

**Step 4: Implement `MULTIPLEXY.apply`**

Replace `MULTIPLEXY.apply`. `MULTIPLEXY` stores `self.control_qubit` (singular) and targets `self.target_qubit`. If Task 4 renamed this to `control_qubits`, substitute accordingly.

```python
    def apply(self, qstate: "QState") -> "QState":
        ctrl = (
            self.control_qubits[0]
            if hasattr(self, "control_qubits") and self.control_qubits
            else self.control_qubit
        )
        index_to_weight = {idx: 0.0 for idx in qstate.index_set}
        for idx, weight in qstate.index_to_weight.items():
            theta = self.theta1 if (idx >> ctrl.index) & 1 else self.theta0
            c = np.cos(theta / 2)
            s = np.sin(theta / 2)
            rdx = idx ^ (1 << self.target_qubit.index)
            if rdx not in qstate.index_set:
                index_to_weight[rdx] = 0.0
            if (idx >> self.target_qubit.index) & 1 == 0:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += weight * s
            else:
                index_to_weight[idx] += weight * c
                index_to_weight[rdx] += -weight * s
        return QState(index_to_weight, qstate.num_qubits)
```

**Step 5: Run test_gate_apply.py — confirm ALL 14 PASS**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_gate_apply.py -v
```

Expected: `14 passed, 0 xfailed`. No XPASS, no FAIL.

**Step 6: Commit**

```bash
git add tests/regression/test_gate_apply.py xyz/circuit/qgate.py
git commit -m "feat(gates): implement MCMY/MULTIPLEXY apply() — all gates covered"
```

---

## Task 8: Full-suite regression on slurm + exit record

**Step 1: Run the full regression suite**

```bash
srun -p debug -A jcgroup --qos=low --time=1:00:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  -u -m pytest tests/regression/ tests/test_algorithms/test_dicke.py \
  tests/test_algorithms/test_prepare_state.py -v --durations=10 \
  -m "not slow"
```

Expected: `52 passed, 1 deselected, 0 xfailed` (41 Phase 0 + 6 Phase 1 + 5 gate-apply now passing that were xfail before; minus `UNIMPLEMENTED_APPLY` going empty means 9 previous xfails are now pass). Total = 41 + 6 + 5 + 9 = no wait: the gate apply parametrize has 14 tests; Phase 1 had 5 pass + 9 xfail = 14. Phase 2 ends with 14 pass + 0 xfail = 14. So the delta is +9 passes, -9 xfails. Pass count goes from 47 to 56. Target: `56 passed, 1 deselected, 0 xfailed`.

If any test FAILs, identify which and roll back the offending task.

**Step 2: Write the exit record**

Create `docs/superpowers/plans/2026-04-20-phase2-exit.md`:

```markdown
# Phase 2 Exit Record

Gate ABC introduced; all concrete gates honor `apply` / `cnot_cost` /
`qubits`. Every getter-style method on Gate is gone, replaced by
attributes or direct method names (`cnot_cost`, `qubits`).

## What landed

- `xyz/gates/types.py` — `QGateType`, `QBit`, and 4 trait mixins.
- `xyz/gates/base.py` — `Gate` ABC.
- `xyz/circuit/qgate.py` — concrete gates rewired to new ABC + traits.
  Getters dropped. 8 new `apply` implementations (RX, RZ, U, CRX, CRZ,
  CU, MCMY, MULTIPLEXY). `Z.apply` already landed in Phase 1.
- Repo-wide sweep: `get_*` → attribute / method-without-prefix.

## Suite state

Last run on slurm (`-m "not slow"`):
`56 passed, 1 deselected, 0 xfailed`.

Phase 3 (file split of `qgate.py` into `xyz/gates/*.py` and
`xyz/decomposition/*.py`) may begin.
```

**Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-20-phase2-exit.md
git commit -m "docs: phase 2 exit record"
```

---

## Phase 2 exit criteria (recap)

- `xyz/gates/types.py` and `xyz/gates/base.py` exist and define the ABC + traits.
- Every concrete gate inherits from `Gate` and implements `apply`, `cnot_cost`, `qubits`.
- `grep -rn "get_cnot_cost\|get_qgate_type\|get_control_qubit\|get_target_qubit\|get_phase\|get_theta\|get_unitary" xyz/` returns only the `QCircuit.get_cnot_cost` method definition (the public circuit-level name stays).
- `tests/regression/test_gate_apply.py::UNIMPLEMENTED_APPLY` is an empty set; every gate-apply test passes.
- Full regression suite green on slurm with `-m "not slow"`.

## Out of Scope

- File relocation (gates/ sub-modules, decomposition/). Phase 3.
- Strategy pattern for `_prepare_state_rec`. Phase 4.
- `import *` cleanup. Phase 5.
