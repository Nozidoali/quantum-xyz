# Phase 3 — Split `qgate.py` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Break the 814-line `xyz/circuit/qgate.py` into focused modules under `xyz/gates/` (concrete gates) and `xyz/decomposition/` (pure-function helpers), then delete `qgate.py`. No behavior change. File-move-only.

**Architecture:** During the split, `xyz/circuit/qgate.py` stays as a shim that re-exports from the new locations so callers keep working mid-phase. The final task (Task 8) deletes the shim, sweeps `from xyz.circuit.qgate import` callsites to the new home, and updates `xyz/circuit/__init__.py` so `xyz.XXX` top-level imports still resolve.

**Tech Stack:** Python 3.10, pytest 8.2. No math changes — Phase 2 finalized all semantics.

**Spec reference:** `docs/superpowers/specs/2026-04-19-refactor-design.md` — "`qgate.py` Decomposition" section and "Phase 3 — Split `qgate.py`" section.

**Base commit:** Phase 2 exit at `d6f6519`. Phase 3 lands on top.

---

## File Structure

**New files** (all inside `xyz/`):

- `xyz/gates/cost_tables.py` — `MCRY_CNOT_COST` table, **int keys** (was string)
- `xyz/gates/single.py` — `X, Z, RX, RY, RZ, U`
- `xyz/gates/controlled.py` — `CX, CRX, CRY, CRZ, CU`
- `xyz/gates/multi_controlled.py` — `MCRY, MCMY, MULTIPLEXY`
- `xyz/decomposition/__init__.py` — empty marker
- `xyz/decomposition/zyz.py` — `to_special_unitary`, `unitary_zyz_decomposition` (moved out of `types.py`)
- `xyz/decomposition/gray_code.py` — `find_thetas`, `decompose_mcry`, `control_sequence_to_gates`
- `xyz/decomposition/mcry.py` — `map_mcry`, `map_mcmy`, `map_muxy`, `map_mcry_linear`, `theta_to_unitary`, `unitary_convert`

**Modified in-place:**

- `xyz/gates/base.py` — `BasicGate` and `AdvancedGate` move here from `qgate.py` (both are pure structural ABC subclasses; they logically belong next to `Gate`)
- `xyz/gates/types.py` — remove the `_to_special_unitary` / `_unitary_zyz_decomposition` helpers (now in `decomposition/zyz.py`); `UnitaryTrait.__init__` imports from the new location
- `xyz/gates/__init__.py` — re-export public names so `from xyz.gates import X, CX, ...` works
- `xyz/circuit/__init__.py` — replace `from .qgate import *` with imports from `xyz.gates` and `xyz.decomposition` so the legacy `from xyz.circuit import Gate, X, ...` surface stays intact

**Deleted:**

- `xyz/circuit/qgate.py` — after Task 8 sweeps remaining imports

---

## Ground rules

- **No behavior change.** Every moved class / function is byte-copied. Imports added inside the copied bodies use the new locations.
- **qgate.py stays as a shim during the migration.** Each move task replaces the moved classes' definitions in `qgate.py` with `from xyz.gates.<new_module> import <names>` lines. Task 8 removes the shim.
- **Regression suite stays green after every task.** Run `pytest tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py` locally after each task; the full slurm run is reserved for Task 9.
- **Use the poetry venv python:** `/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python`.

---

## Task 1: Create `xyz/gates/cost_tables.py` (int keys)

**Files:**
- Create: `xyz/gates/cost_tables.py`
- Modify: `xyz/circuit/qgate.py` (delete the `MCRY_CNOT_COST` module-level dict; update `MCRY.cnot_cost` to import and use the new table)

**Step 1: Write `xyz/gates/cost_tables.py`**

```python
"""Hardcoded CNOT-count lookup for MCRY gates.

The values come from the prior literature's best-known decomposition
counts; the gate's `cnot_cost()` reads them directly. Keys are the
number of control qubits (int), not stringified ints like the original
table in qgate.py."""

from __future__ import annotations

MCRY_CNOT_COST: dict[int, int] = {
    0: 0,
    1: 2,
    2: 4,
    3: 8,
    4: 16,
    5: 32,
    6: 64,
    7: 128,
    8: 226,
    9: 290,
    10: 362,
    11: 442,
    12: 530,
    13: 626,
    14: 730,
    15: 842,
    16: 962,
    17: 1090,
    18: 1226,
    19: 1370,
    20: 1522,
    21: 1682,
    22: 1850,
    23: 2026,
    24: 2210,
    25: 2402,
    26: 2602,
    27: 2810,
    28: 3026,
}
```

**Step 2: Update `MCRY.cnot_cost` in `xyz/circuit/qgate.py`**

Find the current MCRY.cnot_cost (it does `MCRY_CNOT_COST[str(len(self.control_qubits))]` raising ValueError on miss). Change the body to:

```python
    def cnot_cost(self) -> int:
        """Returns the CNOT cost of the gate."""
        from xyz.gates.cost_tables import MCRY_CNOT_COST
        n = len(self.control_qubits)
        if n not in MCRY_CNOT_COST:
            raise ValueError(
                f"MCRY cost table has no entry for n_controls={n}"
            )
        return MCRY_CNOT_COST[n]
```

(The local import is intentional — avoids module-load cycles while qgate.py still holds the concrete class.)

Also **delete** the module-level `MCRY_CNOT_COST = {"0": 0, ...}` dict from `qgate.py` so the old string-keyed version is gone.

**Step 3: Run regression**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `11 passed, 0 xfailed` (6 bug fixes + 5 implemented gate-apply tests; all 14 gate-apply now pass since Phase 2). If an xfail re-appears, the table lookup broke something — inspect.

**Step 4: Commit**

```bash
git add xyz/gates/cost_tables.py xyz/circuit/qgate.py
git commit -m "refactor(gates): extract MCRY cost table to cost_tables.py with int keys"
```

---

## Task 2: Create `xyz/decomposition/zyz.py`

**Files:**
- Create: `xyz/decomposition/__init__.py`
- Create: `xyz/decomposition/zyz.py`
- Modify: `xyz/gates/types.py` (remove the two internal helpers; `UnitaryTrait.__init__` imports from the new module)

**Step 1: Create the package marker**

```bash
: > /home/hanyu/proj/quantum-xyz/xyz/decomposition/__init__.py
```

**Step 2: Write `xyz/decomposition/zyz.py`**

```python
"""Z-Y-Z Euler decomposition of a 1-qubit unitary."""

from __future__ import annotations

import numpy as np
from numpy.linalg import det


def to_special_unitary(matrix: np.ndarray) -> np.ndarray:
    """Normalize a unitary matrix to have determinant 1 (SU(2))."""
    rank = matrix.shape[0]
    return matrix / det(matrix) ** (1 / rank)


def unitary_zyz_decomposition(matrix: np.ndarray):
    """Return the Euler Z-Y-Z decomposition of a 1-qubit unitary.

    Returns a tuple (theta0, theta1, theta2) where the gate equals
    R_z(theta2) @ R_y(theta1) @ R_z(theta0) up to a global phase.
    """
    U = to_special_unitary(matrix)
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

**Step 3: Update `xyz/gates/types.py`**

Inside `UnitaryTrait.__init__`, the line currently reads:

```python
        self.alpha, self.beta, self.gamma = _unitary_zyz_decomposition(unitary)
```

Change to:

```python
        from xyz.decomposition.zyz import unitary_zyz_decomposition
        self.alpha, self.beta, self.gamma = unitary_zyz_decomposition(unitary)
```

Then **delete** the module-level `_to_special_unitary` and `_unitary_zyz_decomposition` functions from `types.py` (at the very bottom of the file). Also remove any `_to_special_unitary_impl` / `_unitary_zyz_decomposition_impl` private aliases if still present.

**Step 4: Keep backwards-compat aliases in `xyz/circuit/qgate.py`**

`qgate.py` currently re-exports `to_special_unitary = _to_special_unitary_impl` and `unitary_zyz_decomposition = _unitary_zyz_decomposition_impl`. Change those to import from the new module:

```python
from xyz.decomposition.zyz import (
    to_special_unitary,
    unitary_zyz_decomposition,
)
```

Remove the old alias lines that reference `_to_special_unitary_impl` / `_unitary_zyz_decomposition_impl`.

**Step 5: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: all pass (no change vs Task 1).

**Step 6: Commit**

```bash
git add xyz/decomposition/__init__.py xyz/decomposition/zyz.py xyz/gates/types.py xyz/circuit/qgate.py
git commit -m "refactor(decomposition): move ZYZ decomposition to xyz/decomposition/zyz.py"
```

---

## Task 3: Create `xyz/decomposition/gray_code.py`

**Files:**
- Create: `xyz/decomposition/gray_code.py`
- Modify: `xyz/circuit/qgate.py` (delete the 3 moved functions; add re-export imports)

**Step 1: Write `xyz/decomposition/gray_code.py`** with exact content (byte-copy from current qgate.py):

```python
"""Gray-code based decomposition of multi-controlled rotations into
single-qubit rotations and CNOTs."""

from __future__ import annotations

from typing import List

import numpy as np
import scipy as sp


def find_thetas(alphas):
    size = len(alphas)
    gray_code_coefficient_matrix = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            bitwise_inner_product = bin(i & (j ^ (j >> 1))).count("1")
            gray_code_coefficient_matrix[i, j] = (-1) ** bitwise_inner_product
    thetas = sp.linalg.solve(gray_code_coefficient_matrix, alphas)
    return thetas


def decompose_mcry(rotation_table: list):
    num_controls = int(np.log2(len(rotation_table)))
    assert num_controls > 0, "The number of controls must be greater than 0"

    alphas = rotation_table[:]
    thetas = find_thetas(alphas)

    control_sequence: list = []
    prev_gray_code = 0

    for i, theta in enumerate(thetas):
        curr_gray_code = ((i + 1) ^ ((i + 1) >> 1)) if i < (2**num_controls) - 1 else 0
        diff = curr_gray_code ^ prev_gray_code
        prev_gray_code = curr_gray_code
        control_id = int(np.log2(diff))
        control_sequence.append((theta, control_id))

    return control_sequence


def control_sequence_to_gates(
    control_sequence: list, control_qubits: list, target_qubit
) -> list:
    # Note: the runtime types of control_qubits / target_qubit / the
    # returned gates come from xyz.gates.* — we keep them loose-typed
    # here to avoid a circular import between decomposition and gates.
    from xyz.gates.controlled import CX
    from xyz.gates.single import RY

    gates: list = []
    for control in control_sequence:
        rotation_theta, control_id = control
        gates.append(RY(rotation_theta, target_qubit))
        gates.append(CX(control_qubits[control_id], 1, target_qubit))
    return gates
```

**IMPORTANT:** `control_sequence_to_gates` currently imports `CX` and `RY` from the same module (qgate.py). After this task the new `xyz.gates.single` and `xyz.gates.controlled` modules don't exist yet (they're created in Tasks 5 and 6). The local imports inside the function body defer resolution — the function only needs them at call time, and by the time anything calls it Tasks 5/6 will have run. Keep the local imports.

**Step 2: Replace the three definitions in `xyz/circuit/qgate.py` with re-exports**

Delete these function definitions from qgate.py (currently around lines 630-705):
- `def find_thetas(alphas): ...`
- `def decompose_mcry(rotation_table): ...`
- `def control_sequence_to_gates(control_sequence, control_qubits, target_qubit): ...`

At the same locations, add:

```python
from xyz.decomposition.gray_code import (
    find_thetas,
    decompose_mcry,
    control_sequence_to_gates,
)
```

**Step 3: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: all pass. If `control_sequence_to_gates` breaks, its RY/CX imports are stale — the current qgate.py should satisfy them via the re-export shim, verify.

**Step 4: Commit**

```bash
git add xyz/decomposition/gray_code.py xyz/circuit/qgate.py
git commit -m "refactor(decomposition): move gray-code helpers to decomposition/gray_code.py"
```

---

## Task 4: Create `xyz/decomposition/mcry.py`

**Files:**
- Create: `xyz/decomposition/mcry.py`
- Modify: `xyz/circuit/qgate.py` (delete the 6 moved functions; add re-export imports)

**Step 1: Write `xyz/decomposition/mcry.py`** with content copied from the current qgate.py:

```python
"""Mapping of multi-controlled rotation gates to primitive sequences."""

from __future__ import annotations

from collections import namedtuple
from typing import List

import numpy as np

from xyz.decomposition.gray_code import (
    control_sequence_to_gates,
    decompose_mcry,
)
from xyz.gates.types import QGateType


def theta_to_unitary(theta: float):
    raw_matrix = np.array(
        [
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2), np.cos(theta / 2)],
        ]
    )
    return raw_matrix


def unitary_convert(unitary: np.ndarray, coef: float, signal: int):
    param = 1 / np.abs(coef)
    values, vectors = np.linalg.eig(unitary)
    updated_unitary = (
        np.power(values[0] + 0j, param) * vectors[:, [0]] @ vectors[:, [0]].conj().T
    )
    updated_unitary = (
        updated_unitary
        + np.power(values[1] + 0j, param) * vectors[:, [1]] @ vectors[:, [1]].conj().T
    )
    if signal < 0:
        updated_unitary = np.linalg.inv(updated_unitary)
    return updated_unitary


def map_muxy(gate) -> list:
    assert gate.qgate_type == QGateType.MULTIPLEX_Y
    rotation_table = [gate.theta0, gate.theta1]
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(
        control_sequence, [gate.control_qubits[0]], gate.target_qubit
    )
    return gates


def map_mcry(gate) -> list:
    match gate.qgate_type:
        case QGateType.MCRY:
            control_qubits = gate.control_qubits
            phases = gate.phases
            target_qubit = gate.target_qubit
        case QGateType.CRY:
            control_qubits = list(gate.control_qubits)
            phases = [gate.phase]
            target_qubit = gate.target_qubit
        case _:
            raise ValueError("Not a MCRY gate")
    rotation_table = np.zeros(2 ** (len(control_qubits)))
    rotated_index = 0
    for i, controlled_by_one in enumerate(phases):
        if controlled_by_one is True:
            rotated_index += 2**i

    rotation_table[rotated_index] = gate.theta
    control_sequence = decompose_mcry(rotation_table)
    gates = control_sequence_to_gates(control_sequence, control_qubits, target_qubit)
    return gates


def map_mcmy(gate) -> list:
    rotation_table = gate.rotation_table
    control_sequence = decompose_mcry(rotation_table=rotation_table)
    gates = control_sequence_to_gates(
        control_sequence,
        gate.control_qubits,
        gate.target_qubit,
    )
    return gates


def map_mcry_linear(mcry_gate) -> list:
    from xyz.gates.single import X
    from xyz.gates.controlled import CRX, CU

    assert mcry_gate.qgate_type == QGateType.MCRY

    qubit_list = list(mcry_gate.control_qubits) + [mcry_gate.target_qubit]
    num_qubits = len(qubit_list)

    if num_qubits == 1:
        from xyz.gates.single import RY
        return [RY(mcry_gate.theta, qubit_list[0])]

    def convert_rec(
        unitary: np.ndarray, num_qubits: int, is_first: bool = True, step: int = 1
    ):
        nonlocal qubit_list
        pairs = namedtuple("pairs", ["control", "target"])
        if step == 1:
            start = 0
            reverse = True
        else:
            start = 1
            reverse = False
        qubit_pairs = [
            pairs(control, target)
            for target in range(num_qubits)
            for control in range(start, target)
        ]
        qubit_pairs.sort(key=lambda e: e.control + e.target, reverse=reverse)
        gates: list = []
        for pair in qubit_pairs:
            exponent = pair.target - pair.control
            if pair.control == 0:
                exponent = exponent - 1
            param = 2**exponent
            signal = -1 if (pair.control == 0 and not is_first) else 1
            signal = signal * step

            if pair.target == num_qubits - 1 and is_first:
                updated_unitary = unitary_convert(unitary, param, signal)
                gate = CU(
                    updated_unitary,
                    qubit_list[pair.control],
                    True,
                    qubit_list[pair.target],
                )
                gates.append(gate)
            else:
                gate = CRX(
                    signal * np.pi / param,
                    qubit_list[pair.control],
                    True,
                    qubit_list[pair.target],
                )
                gates.append(gate)

        return gates

    unitary = theta_to_unitary(mcry_gate.theta)

    gates: list = []
    for phase, control_qubit in zip(mcry_gate.phases, mcry_gate.control_qubits):
        if phase == 0:
            gates.append(X(control_qubit))

    gates_c1 = convert_rec(unitary, num_qubits)
    gates_c2 = convert_rec(unitary, num_qubits, step=-1)
    gates_c3 = convert_rec(unitary, num_qubits - 1, is_first=False)
    gates_c4 = convert_rec(unitary, num_qubits - 1, is_first=False, step=-1)

    gates.extend(gates_c1)
    gates.extend(gates_c2)
    gates.extend(gates_c3)
    gates.extend(gates_c4)

    for phase, control_qubit in zip(mcry_gate.phases, mcry_gate.control_qubits):
        if phase == 0:
            gates.append(X(control_qubit))
    return gates
```

**Step 2: Delete the 6 functions from `xyz/circuit/qgate.py`**

Remove these function definitions from qgate.py (currently around lines 591+):
- `def map_muxy(gate)`
- `def map_mcry(gate)`
- `def map_mcmy(gate)`
- `def theta_to_unitary(theta)`
- `def unitary_convert(unitary, coef, signal)`
- `def map_mcry_linear(mcry_gate)`

Add a re-export block at the same location:

```python
from xyz.decomposition.mcry import (
    map_muxy,
    map_mcry,
    map_mcmy,
    map_mcry_linear,
    theta_to_unitary,
    unitary_convert,
)
```

**Step 3: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: all 11 pass (in particular `test_map_muxy_does_not_raise_attribute_error` still passes — the moved `map_muxy` still uses `gate.qgate_type`, the Phase 1 fix).

**Step 4: Commit**

```bash
git add xyz/decomposition/mcry.py xyz/circuit/qgate.py
git commit -m "refactor(decomposition): move mapper helpers to decomposition/mcry.py"
```

---

## Task 5: Create `xyz/gates/single.py`

**Files:**
- Create: `xyz/gates/single.py`
- Modify: `xyz/circuit/qgate.py` (delete 6 gate classes; add re-export imports)

**Step 1: Write `xyz/gates/single.py`** — copy X, Z, RX, RY, RZ, U classes exactly from their current location in qgate.py. Use the current (Phase 2) implementation of each — DO NOT re-derive `apply` bodies. Copy verbatim.

Top of file:

```python
"""Single-qubit concrete gates: X, Z, RX, RY, RZ, U."""

from __future__ import annotations

from typing import List

import numpy as np

from xyz.circuit.qstate import QState
from xyz.gates.base import BasicGate, Gate
from xyz.gates.types import QBit, QGateType, RotationTrait, UnitaryTrait
```

**CAVEAT — `BasicGate` is not yet in `xyz.gates.base`.** It's still in `qgate.py` at this point; Task 8 moves it. Use a temporary import to keep the migration working:

```python
# Task 8 moves BasicGate into xyz.gates.base. Until then, import from
# the transitional location:
from xyz.circuit.qgate import BasicGate
```

Replace the earlier `from xyz.gates.base import BasicGate, Gate` line with:

```python
from xyz.gates.base import Gate  # noqa: F401 — stub for future use
from xyz.circuit.qgate import BasicGate
```

Then paste the 6 gate classes from qgate.py. Each inherits from `BasicGate` (plus `RotationTrait` or `UnitaryTrait` as appropriate). Body is byte-for-byte the current Phase 2 version. No math changes.

**Step 2: Replace the 6 class definitions in `xyz/circuit/qgate.py` with re-export imports**

Delete `class X`, `class Z`, `class RX`, `class RY`, `class RZ`, `class U` from `qgate.py`.

At the same location (or grouped at the bottom), add:

```python
from xyz.gates.single import X, Z, RX, RY, RZ, U  # noqa: F401
```

**Step 3: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: 11 pass (gate_apply tests for X, Z, RX, RY, RZ, U all still pass — they now live in `single.py` but the shim in `qgate.py` keeps the `from xyz.circuit.qgate import X` path alive).

**Step 4: Commit**

```bash
git add xyz/gates/single.py xyz/circuit/qgate.py
git commit -m "refactor(gates): extract single-qubit gates to xyz/gates/single.py"
```

---

## Task 6: Create `xyz/gates/controlled.py`

**Files:**
- Create: `xyz/gates/controlled.py`
- Modify: `xyz/circuit/qgate.py`

**Step 1: Write `xyz/gates/controlled.py`** — copy CX, CRX, CRY, CRZ, CU classes verbatim from current qgate.py.

Top of file:

```python
"""Singly-controlled concrete gates: CX, CRX, CRY, CRZ, CU."""

from __future__ import annotations

from typing import List

import numpy as np

from xyz.circuit.qstate import QState
from xyz.gates.base import Gate  # noqa: F401
from xyz.circuit.qgate import BasicGate  # Task 8 moves this
from xyz.gates.types import QBit, QGateType, RotationTrait, UnitaryTrait, ControlledTrait
```

Paste the 5 controlled-gate classes. Each declares inheritance `(BasicGate, ControlledTrait)` or `(BasicGate, RotationTrait, ControlledTrait)` or `(BasicGate, UnitaryTrait, ControlledTrait)` as currently in qgate.py. Body byte-for-byte.

**Step 2: Replace in `xyz/circuit/qgate.py`**

Delete `class CX`, `class CRX`, `class CRY`, `class CRZ`, `class CU` from qgate.py. Add:

```python
from xyz.gates.controlled import CX, CRX, CRY, CRZ, CU  # noqa: F401
```

**Step 3: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: 11 pass.

**Step 4: Commit**

```bash
git add xyz/gates/controlled.py xyz/circuit/qgate.py
git commit -m "refactor(gates): extract singly-controlled gates to xyz/gates/controlled.py"
```

---

## Task 7: Create `xyz/gates/multi_controlled.py`

**Files:**
- Create: `xyz/gates/multi_controlled.py`
- Modify: `xyz/circuit/qgate.py`

**Step 1: Write `xyz/gates/multi_controlled.py`** — copy MCRY, MCMY, MULTIPLEXY classes verbatim from current qgate.py.

Top of file:

```python
"""Multi-controlled and multiplexed concrete gates: MCRY, MCMY, MULTIPLEXY."""

from __future__ import annotations

from typing import List

import numpy as np

from xyz.circuit.qstate import QState
from xyz.gates.base import Gate  # noqa: F401
from xyz.circuit.qgate import BasicGate, AdvancedGate  # Task 8 moves these
from xyz.gates.types import (
    QBit,
    QGateType,
    RotationTrait,
    MultiControlledTrait,
)
```

Paste the 3 classes. MCRY inherits `(BasicGate, RotationTrait, MultiControlledTrait)`. MCMY and MULTIPLEXY inherit from `AdvancedGate`.

Leave `MCRY.cnot_cost` as-is (it imports MCRY_CNOT_COST locally from Task 1). Leave MULTIPLEXY's `self.control_qubits = [control_qubit]` line (Phase 2 added that).

**Step 2: Replace in `xyz/circuit/qgate.py`**

Delete `class MCRY`, `class MCMY`, `class MULTIPLEXY` from qgate.py. Add:

```python
from xyz.gates.multi_controlled import MCRY, MCMY, MULTIPLEXY  # noqa: F401
```

**Step 3: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: 11 pass. Note: `test_map_muxy_does_not_raise_attribute_error` still uses `from xyz.circuit.qgate import MULTIPLEXY, QBit, map_muxy` — still works via the shim.

**Step 4: Commit**

```bash
git add xyz/gates/multi_controlled.py xyz/circuit/qgate.py
git commit -m "refactor(gates): extract multi-controlled gates to xyz/gates/multi_controlled.py"
```

---

## Task 8: Move BasicGate/AdvancedGate to base.py; delete qgate.py; sweep imports

**Files:**
- Modify: `xyz/gates/base.py` (add BasicGate, AdvancedGate)
- Modify: `xyz/gates/single.py`, `xyz/gates/controlled.py`, `xyz/gates/multi_controlled.py` (replace `from xyz.circuit.qgate import BasicGate/AdvancedGate` with `from xyz.gates.base import ...`)
- Modify: `xyz/gates/__init__.py` (re-export gate classes)
- Modify: `xyz/circuit/__init__.py` (replace `from .qgate import *` with imports from `xyz.gates.*`)
- Sweep: every `from xyz.circuit.qgate import ...` in `xyz/`, `tests/`, `example/` → point to the new homes
- Delete: `xyz/circuit/qgate.py`

**Step 1: Move BasicGate and AdvancedGate into `xyz/gates/base.py`**

Open `xyz/gates/base.py`. Currently it contains only the `Gate` ABC. Append (at the bottom of the file):

```python
from xyz.gates.types import QBit


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

    Subclasses provide `apply`, `cnot_cost`, `qubits` themselves.
    """
    # no extra state — Gate.__init__ does the work
```

Note: we are **tightening the contract** from the original `BasicGate` which had an `assert isinstance` — replaced with a `raise TypeError` since `assert` gets stripped in optimized builds. Also dropping the `get_target_qubit` method (already dropped in Phase 2's Task 4 sweep).

**Step 2: Update the three new gate files to import from base.py**

In each of `xyz/gates/single.py`, `xyz/gates/controlled.py`, `xyz/gates/multi_controlled.py`, find:

```python
from xyz.circuit.qgate import BasicGate  # Task 8 moves this
```

or

```python
from xyz.circuit.qgate import BasicGate, AdvancedGate  # Task 8 moves these
```

Replace with:

```python
from xyz.gates.base import BasicGate
```

or (for multi_controlled.py):

```python
from xyz.gates.base import BasicGate, AdvancedGate
```

Remove the old comments about "Task 8 moves this".

**Step 3: Populate `xyz/gates/__init__.py`**

It's currently empty. Replace with:

```python
"""Public gate API: re-exports every concrete gate and the Gate ABC."""

from xyz.gates.base import AdvancedGate, BasicGate, Gate
from xyz.gates.controlled import CRX, CRY, CRZ, CU, CX
from xyz.gates.multi_controlled import MCMY, MCRY, MULTIPLEXY
from xyz.gates.single import RX, RY, RZ, U, X, Z
from xyz.gates.types import (
    ControlledTrait,
    MultiControlledTrait,
    QBit,
    QGateType,
    RotationTrait,
    UnitaryTrait,
)

__all__ = [
    "AdvancedGate", "BasicGate", "Gate",
    "CRX", "CRY", "CRZ", "CU", "CX",
    "MCMY", "MCRY", "MULTIPLEXY",
    "RX", "RY", "RZ", "U", "X", "Z",
    "ControlledTrait", "MultiControlledTrait",
    "QBit", "QGateType",
    "RotationTrait", "UnitaryTrait",
]
```

**Step 4: Replace `xyz/circuit/__init__.py`'s `from .qgate import *`**

Open `xyz/circuit/__init__.py`. Current contents (approx):

```python
from .qstate import *
from .qgate import *
from .qcircuit import *
```

Replace the `.qgate` line with imports from `xyz.gates` and `xyz.decomposition`:

```python
from .qstate import *
from .qcircuit import *
from xyz.gates import *  # re-export so `from xyz.circuit import X` keeps working
from xyz.decomposition.mcry import (
    map_muxy, map_mcry, map_mcmy, map_mcry_linear,
    theta_to_unitary, unitary_convert,
)
from xyz.decomposition.gray_code import (
    find_thetas, decompose_mcry, control_sequence_to_gates,
)
from xyz.decomposition.zyz import to_special_unitary, unitary_zyz_decomposition
```

(The `MultiRotationGate` class in qgate.py is not re-exported anywhere and appears unused. If pytest fails because something imports it, add `from xyz.circuit.qgate import MultiRotationGate` to the circuit __init__ AND keep a stub qgate.py with only that class — otherwise delete it entirely.)

**Step 5: Sweep callers of `from xyz.circuit.qgate import ...`**

```bash
grep -rln "from xyz.circuit.qgate import\|from .qgate import" xyz tests example | grep -v __pycache__ | grep -v docs
```

For each file, replace the import path. Target:
- Single-qubit gates (X, Z, RX, RY, RZ, U) → `from xyz.gates.single import ...`
- Controlled gates (CX, CRX, CRY, CRZ, CU) → `from xyz.gates.controlled import ...`
- Multi-controlled (MCRY, MCMY, MULTIPLEXY) → `from xyz.gates.multi_controlled import ...`
- Traits / QBit / QGateType → `from xyz.gates.types import ...`
- `BasicGate` / `AdvancedGate` / `Gate` → `from xyz.gates.base import ...`
- `QGate` → remove (it was a legacy alias for `Gate`; callers should use `Gate` from `xyz.gates.base`)
- Helpers (`map_muxy`, `find_thetas`, etc.) → `from xyz.decomposition.<mcry|gray_code|zyz> import ...`
- `to_special_unitary`, `unitary_zyz_decomposition` → `from xyz.decomposition.zyz import ...`
- `MCRY_CNOT_COST` → `from xyz.gates.cost_tables import MCRY_CNOT_COST`

If a single import statement pulls names from multiple destinations, split into two or more imports.

Example rewrites you will likely see:

`tests/regression/test_bug_fixes.py`:

```python
# Before
from xyz.circuit.qgate import QBit, Z
from xyz.circuit.qgate import MULTIPLEXY, QBit, map_muxy

# After
from xyz.gates.single import Z
from xyz.gates.multi_controlled import MULTIPLEXY
from xyz.gates.types import QBit
from xyz.decomposition.mcry import map_muxy
```

`tests/regression/test_gate_apply.py`:

```python
# Before
from xyz.circuit.qgate import (
    CRX, CRY, CRZ, CU, CX, MCMY, MCRY, MULTIPLEXY,
    QBit, RX, RY, RZ, U, X, Z,
)

# After
from xyz.gates.controlled import CRX, CRY, CRZ, CU, CX
from xyz.gates.multi_controlled import MCMY, MCRY, MULTIPLEXY
from xyz.gates.single import RX, RY, RZ, U, X, Z
from xyz.gates.types import QBit
```

**Step 6: Verify nothing still imports from `xyz.circuit.qgate`**

```bash
grep -rn "xyz.circuit.qgate\|from \.qgate" xyz tests example | grep -v __pycache__ | grep -v "docs/"
```

Expected: empty.

**Step 7: Delete `xyz/circuit/qgate.py`**

```bash
rm /home/hanyu/proj/quantum-xyz/xyz/circuit/qgate.py
```

**Step 8: Regression check**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/ -v -m "not slow"
```

Expected: `44 passed, 1 deselected, 0 xfailed` (10 dense + 15 sparse + 5 dicke + 14 gate_apply = 44 — wait, Phase 2's count was 56 for the full suite including legacy dicke + prepare_state::test_qsp_2. Re-check the current number. The regression-only count should be 10+15+5+14+6 bug-fix = 50 passed.)

Actually: tests/regression/ contains dense (10) + sparse (15) + dicke (5) + gate_apply (14 pass post-Phase-2) + bug_fixes (6) = 50.

So expected: `50 passed, 0 xfailed` (the `test_qsp_1` slow skip is in `tests/test_algorithms/`, not `tests/regression/`, so it's not deselected here).

If anything fails with `ImportError` about qgate or an unresolved name, the sweep missed a caller — grep and fix it.

**Step 9: Commit**

```bash
git add -u
git add xyz/gates/__init__.py xyz/gates/base.py xyz/gates/single.py xyz/gates/controlled.py xyz/gates/multi_controlled.py xyz/circuit/__init__.py
git rm xyz/circuit/qgate.py 2>/dev/null || true
git commit -m "refactor(gates): move BasicGate/AdvancedGate to base.py, delete qgate.py, sweep imports"
```

---

## Task 9: Full-suite slurm verification + exit record

**Step 1: Run the full regression + legacy suite on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=1:00:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  -u -m pytest tests/regression/ tests/test_algorithms/test_dicke.py \
  tests/test_algorithms/test_prepare_state.py -v --durations=10 \
  -m "not slow"
```

Expected: `56 passed, 1 deselected, 0 xfailed` — unchanged from Phase 2's exit (the split is byte-preserving). Runtime under 10s.

If anything fails, it's an import-sweep miss from Task 8. Fix and re-run.

**Step 2: Verify qgate.py is gone and the new structure is in place**

```bash
test ! -f /home/hanyu/proj/quantum-xyz/xyz/circuit/qgate.py && echo "qgate.py deleted"
ls /home/hanyu/proj/quantum-xyz/xyz/gates/
ls /home/hanyu/proj/quantum-xyz/xyz/decomposition/
wc -l /home/hanyu/proj/quantum-xyz/xyz/gates/*.py
```

Expected:
- `qgate.py deleted`
- `xyz/gates/`: `__init__.py base.py controlled.py cost_tables.py multi_controlled.py single.py types.py` (7 files)
- `xyz/decomposition/`: `__init__.py gray_code.py mcry.py zyz.py` (4 files)
- Every file in `xyz/gates/` has under 200 lines.

**Step 3: Write the exit record**

Create `docs/superpowers/plans/2026-04-20-phase3-exit.md`:

```markdown
# Phase 3 Exit Record

`xyz/circuit/qgate.py` is gone. Concrete gates live in `xyz/gates/`,
helpers in `xyz/decomposition/`.

## New structure

- `xyz/gates/base.py` — `Gate` ABC, `BasicGate`, `AdvancedGate`
- `xyz/gates/types.py` — `QGateType`, `QBit`, 4 trait mixins
- `xyz/gates/cost_tables.py` — `MCRY_CNOT_COST` (int keys)
- `xyz/gates/single.py` — `X, Z, RX, RY, RZ, U`
- `xyz/gates/controlled.py` — `CX, CRX, CRY, CRZ, CU`
- `xyz/gates/multi_controlled.py` — `MCRY, MCMY, MULTIPLEXY`
- `xyz/decomposition/zyz.py` — `to_special_unitary`, `unitary_zyz_decomposition`
- `xyz/decomposition/gray_code.py` — `find_thetas`, `decompose_mcry`, `control_sequence_to_gates`
- `xyz/decomposition/mcry.py` — `map_muxy`, `map_mcry`, `map_mcmy`, `map_mcry_linear`, `theta_to_unitary`, `unitary_convert`

Every file in `xyz/gates/` is under 200 lines.

## Suite state

Last slurm run on `-m "not slow"`:
`56 passed, 1 deselected, 0 xfailed` — unchanged from Phase 2.

Phase 4 (strategy pattern for `prepare_state`, reorganization of
`algorithms/` → `synthesis/`, `external/` → `io/`) may begin.
```

**Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-04-20-phase3-exit.md
git commit -m "docs: phase 3 exit record"
```

---

## Phase 3 exit criteria (recap)

- `xyz/circuit/qgate.py` does not exist.
- `xyz/gates/` contains 7 files, each under 200 lines.
- `xyz/decomposition/` contains 4 files.
- `xyz/gates/__init__.py` has explicit `__all__`.
- `xyz/circuit/__init__.py` re-exports from `xyz.gates` / `xyz.decomposition`.
- `grep -rn "xyz.circuit.qgate\|from \.qgate" xyz tests example` is empty.
- `56 passed, 1 deselected, 0 xfailed` on slurm.

## Out of Scope

- Strategy pattern for `_prepare_state_rec`. Phase 4.
- Package reorganization (algorithms/ → synthesis/, external/ → io/). Phase 4.
- Explicit `__all__` in other `__init__.py` files. Phase 5.
