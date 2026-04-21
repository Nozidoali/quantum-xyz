# Phase 5 — `import *` Cleanup + Public API Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every `from x import *` in `xyz/` with an explicit `from x import <names>` list backed by an `__all__` declaration. Pin `xyz/__init__.py` to the 9 public symbols the spec commits to. Delete the legacy backwards-compat aliases accumulated through Phases 2–4.

**Architecture:** Sub-package `__init__.py` files get explicit `__all__` + explicit re-exports. Top-level `xyz/__init__.py` drops the `import *` chain and imports the 9 public names directly from their home modules. Legacy aliases (`QGate = Gate`, `__Stats = Stats`, etc.) are deleted.

**Tech Stack:** Python 3.10, pytest 8.2. No new deps.

**Spec reference:** `docs/superpowers/specs/2026-04-19-refactor-design.md` — "Phase 5 — Explicit Exports" section.

**Base commit:** Phase 4 exit at `99a33a4`. Phase 5 lands on top.

---

## Current `import *` inventory

11 star-imports exist in source code today:

| File | Line | Statement |
|---|---|---|
| `xyz/__init__.py` | 1–6 | `from .synthesis import *` and 5 others |
| `xyz/circuit/__init__.py` | 4–6 | 3 star imports |
| `xyz/circuit/qcircuit.py` | 4 | `from xyz.gates import *` |
| `xyz/synthesis/__init__.py` | 1–5 | 5 star imports |
| `xyz/synthesis/support_reduction/__init__.py` | 10–12 | 3 star imports |
| `xyz/passes/__init__.py` | 1–2 | 2 star imports |
| `xyz/passes/mapping.py` | 6 | `from xyz.circuit import *` |
| `xyz/io/__init__.py` | 10–14 | 5 star imports |
| `xyz/utils/__init__.py` | 10–11 | 2 star imports |
| `xyz/state/__init__.py` | 3 | `from xyz.state.qstate import *` |
| `xyz/decomposition/__init__.py` | — | empty, needs nothing but stays empty |

Plus: legacy alias lines scattered across `xyz/gates/__init__.py` (5 aliases) and `xyz/synthesis/prepare_state.py` (`__Stats = Stats`).

## Public API (what `xyz/__init__.py` will export)

Per the spec, exactly 9 symbols at the top level:

1. `prepare_state`
2. `QState`
3. `QCircuit`
4. `quantize_state`
5. `simulate_circuit`
6. `to_qiskit`
7. `StatePreparationParameters`
8. `stopwatch`
9. `D_state`

All other names stay importable from their sub-packages (e.g. `from xyz.gates import X, CX`), but NOT from the top-level `xyz`.

---

## Ground rules

- **Behavior preserved end-to-end.** Any test that passed before Phase 5 must still pass. `example/synthesize_dicke.py` must still run.
- **Per-task local regression**: `pytest tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py` after each task (sub-second).
- **Full slurm verification in Task 6** (final task).
- **Poetry venv python** throughout: `/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python`.

---

## Task 1: Add `__all__` to leaf modules that currently lack one

Sub-modules under `synthesis/`, `passes/`, `io/`, `utils/`, `state/` get explicit `__all__` declarations at the top of the file (just below the docstring). This enables the `__init__.py` files in later tasks to replace `import *` with explicit imports that match.

**Files to edit** (add an `__all__` near the top of each):

- `xyz/synthesis/prepare_state.py` — public: `prepare_state`, `StatePreparationParameters`, `Stats`, `__Stats` (legacy)
- `xyz/synthesis/n_flow.py` — public: `qubit_reduction`, `qubit_decomposition`, `select_pivot_qubit`, `select_informative_qubit`, `to_controlled_gate`
- `xyz/synthesis/sparse_state_synthesis.py` — public: `cardinality_reduction`, `depth_optimized_cardinality_reduction`, `sparse_state_synthesis`, `parallel_sparse_state_synthesis`
- `xyz/synthesis/exact_cnot_synthesis.py` — public: `exact_cnot_synthesis`, `QSPDatabase`, `AStarCost`, `Explorer`, `get_state_transitions`, `backtrace`
- `xyz/synthesis/deterministic_dicke_state.py` — public: `prepare_dicke_state`, `SCSManager`, `TriState`, `D_state` (the xyz.D_state function lives in `xyz/state/qstate.py` — check). NOTE: `D_state` is in `qstate.py`, not here — confirm via grep.
- `xyz/synthesis/support_reduction/support_reduction.py` — public: `support_reduction`, `x_reduction` (check via grep; `x_reduction` may be in `x_reduction.py`)
- `xyz/synthesis/support_reduction/x_reduction.py` — public: `x_reduction`
- `xyz/synthesis/support_reduction/ry_reduction.py` — public: look at actual defs
- `xyz/passes/resynthesis.py` — public: `resynthesis`, `resub0`, `resubA`, `resub1`, `resubN`, `resub2N`, `resubN_trypass`, `resynthesize_window`, `extract_windows_naive`, `extract_windows`, `LstSqSolver`, `LstSqSolverVar`, `try_resub`, `get_candidate_controls`
- `xyz/passes/mapping.py` — public: `mapping`, `mapping_debug`, `schedule_commutable_gates`, `to_dag`, `QNode`, `QNetwork`, `Mapper`, `ChoiceNode`, `ChoiceType`
- `xyz/io/simulate_circuit.py` — public: `simulate_circuit`
- `xyz/io/to_qiskit.py` — public: `to_qiskit`, `qiskit_depth_evaluation`
- `xyz/io/special_gates.py` — public: whatever it defines (check via grep)
- `xyz/io/write_qasm.py` — public: `write_qasm`
- `xyz/io/read_qasm.py` — public: `read_qasm`
- `xyz/io/qiskit_opt.py` — public: whatever it defines
- `xyz/utils/timer.py` — public: `stopwatch`, `GlobalStopwatch`, `call_with_global_timer`, `get_time`, `global_stopwatch_report`
- `xyz/utils/colors.py` — public: `print_green`, `print_red`, `print_yellow`, `text_red`, `text_yellow`, `print_blue`, `print_orange`, `text_orange`
- `xyz/state/qstate.py` — public: `QState`, `quantize_state`, `D_state`, plus any other helpers

The pattern, applied to each file (example for `xyz/utils/timer.py`):

```python
# (existing docstring / shebang lines stay)

__all__ = [
    "stopwatch",
    "GlobalStopwatch",
    "call_with_global_timer",
    "get_time",
    "global_stopwatch_report",
]

# (existing imports and code stay unchanged)
```

Place `__all__` immediately after the module docstring (or at the top of the file if there's no docstring). Do NOT change any code — only add the declaration.

- [ ] **Step 1: Enumerate each module's public symbols**

For each file listed above, use `grep` to find top-level `def` / `class` definitions that do NOT start with an underscore:

```bash
grep -n "^def [^_]\|^class [^_]" <file>
```

Compose an `__all__` list of those names.

- [ ] **Step 2: Add `__all__` to each file**

For each file, read it and add the `__all__` block near the top (after the docstring).

- [ ] **Step 3: Run local regression to confirm nothing broke**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `20 passed`. `__all__` alone doesn't change imports (old `import *` still works; it just filters to the listed names).

- [ ] **Step 4: Commit**

```bash
git add -u
git commit -m "refactor(exports): add explicit __all__ to leaf modules"
```

---

## Task 2: Replace `import *` in sub-package `__init__.py` files

Convert each sub-package's `__init__.py` from a stack of `import *` lines to explicit imports, backed by an `__all__` that aggregates the sub-module `__all__` lists.

**Files to rewrite:**

### 2a. `xyz/utils/__init__.py`

Current:

```python
#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""..."""

from .colors import *
from .timer import *
```

Replace with:

```python
"""Shared utilities: color printing, stopwatch."""

from xyz.utils.colors import (
    print_green,
    print_red,
    print_yellow,
    text_red,
    text_yellow,
    print_blue,
    print_orange,
    text_orange,
)
from xyz.utils.timer import (
    stopwatch,
    GlobalStopwatch,
    call_with_global_timer,
    get_time,
    global_stopwatch_report,
)

__all__ = [
    # colors
    "print_green", "print_red", "print_yellow",
    "text_red", "text_yellow",
    "print_blue", "print_orange", "text_orange",
    # timer
    "stopwatch", "GlobalStopwatch", "call_with_global_timer",
    "get_time", "global_stopwatch_report",
]
```

### 2b. `xyz/state/__init__.py`

Replace:

```python
"""Quantum state data types."""

from xyz.state.qstate import *  # noqa: F401,F403
```

With:

```python
"""Quantum state data types."""

from xyz.state.qstate import QState, quantize_state, D_state

__all__ = ["QState", "quantize_state", "D_state"]
```

(If `qstate.py` exports more symbols, include them; the list above is the minimum per the public API.)

### 2c. `xyz/synthesis/__init__.py`

Replace the 5-line `import *` chain with explicit imports. Full content:

```python
"""Quantum state preparation synthesis."""

from xyz.synthesis.prepare_state import (
    prepare_state,
    StatePreparationParameters,
    Stats,
)
from xyz.synthesis.deterministic_dicke_state import prepare_dicke_state
from xyz.synthesis.exact_cnot_synthesis import exact_cnot_synthesis
from xyz.synthesis.n_flow import qubit_reduction, qubit_decomposition
from xyz.synthesis.sparse_state_synthesis import (
    cardinality_reduction,
    sparse_state_synthesis,
)

__all__ = [
    "prepare_state",
    "StatePreparationParameters",
    "Stats",
    "prepare_dicke_state",
    "exact_cnot_synthesis",
    "qubit_reduction",
    "qubit_decomposition",
    "cardinality_reduction",
    "sparse_state_synthesis",
]
```

### 2d. `xyz/synthesis/support_reduction/__init__.py`

Replace:

```python
#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""..."""

from .x_reduction import *
from .ry_reduction import *
from .support_reduction import *
```

With (names based on Step 1's enumeration — adjust if actual defs differ):

```python
"""Support-reduction preprocessing for state preparation."""

from xyz.synthesis.support_reduction.x_reduction import x_reduction
from xyz.synthesis.support_reduction.ry_reduction import ry_reduction
from xyz.synthesis.support_reduction.support_reduction import support_reduction

__all__ = ["x_reduction", "ry_reduction", "support_reduction"]
```

If `ry_reduction.py` actually defines different names, enumerate via grep and include them.

### 2e. `xyz/passes/__init__.py`

Replace:

```python
from .resynthesis import *
from .mapping import *
```

With:

```python
"""Circuit optimization passes."""

from xyz.passes.resynthesis import resynthesis
from xyz.passes.mapping import mapping, mapping_debug, schedule_commutable_gates

__all__ = [
    "resynthesis",
    "mapping",
    "mapping_debug",
    "schedule_commutable_gates",
]
```

### 2f. `xyz/io/__init__.py`

Replace the 5-line `import *` chain with:

```python
"""I/O: qiskit interop + QASM read/write + simulation."""

from xyz.io.simulate_circuit import simulate_circuit
from xyz.io.to_qiskit import to_qiskit, qiskit_depth_evaluation
from xyz.io.write_qasm import write_qasm
from xyz.io.read_qasm import read_qasm

__all__ = [
    "simulate_circuit",
    "to_qiskit",
    "qiskit_depth_evaluation",
    "write_qasm",
    "read_qasm",
]
```

(Skip `special_gates.py` and `qiskit_opt.py` from the public API unless step 1's enumeration reveals they're consumed elsewhere. If consumed, add the explicit imports.)

### 2g. `xyz/circuit/__init__.py`

Replace the 3-line `import *` chain with explicit imports. The current file also has explicit decomposition imports — keep those. Full content:

```python
"""Circuit: gates, state, container, and the qiskit-interop decomposition helpers."""

from xyz.state.qstate import QState, quantize_state, D_state
from xyz.circuit.qcircuit import QCircuit
from xyz.gates import (
    Gate, BasicGate, AdvancedGate,
    X, Z, RX, RY, RZ, U,
    CX, CRX, CRY, CRZ, CU,
    MCRY, MCMY, MULTIPLEXY,
    QBit, QGateType,
    RotationTrait, UnitaryTrait, ControlledTrait, MultiControlledTrait,
)
from xyz.decomposition.mcry import (
    map_muxy, map_mcry, map_mcmy, map_mcry_linear,
    theta_to_unitary, unitary_convert,
)
from xyz.decomposition.gray_code import (
    find_thetas, decompose_mcry, control_sequence_to_gates,
)
from xyz.decomposition.zyz import to_special_unitary, unitary_zyz_decomposition

__all__ = [
    # state
    "QState", "quantize_state", "D_state",
    # circuit
    "QCircuit",
    # gates (re-export)
    "Gate", "BasicGate", "AdvancedGate",
    "X", "Z", "RX", "RY", "RZ", "U",
    "CX", "CRX", "CRY", "CRZ", "CU",
    "MCRY", "MCMY", "MULTIPLEXY",
    "QBit", "QGateType",
    "RotationTrait", "UnitaryTrait", "ControlledTrait", "MultiControlledTrait",
    # decomposition
    "map_muxy", "map_mcry", "map_mcmy", "map_mcry_linear",
    "theta_to_unitary", "unitary_convert",
    "find_thetas", "decompose_mcry", "control_sequence_to_gates",
    "to_special_unitary", "unitary_zyz_decomposition",
]
```

### 2h. `xyz/circuit/qcircuit.py`

Replace line 4:

```python
from xyz.gates import *
```

With the explicit imports that qcircuit.py actually uses. First determine them:

```bash
grep -n "^from\|^import\| X(\| Z(\| RY(\| CX(\| QGateType\." xyz/circuit/qcircuit.py | head -20
```

Then replace the star with explicit names like:

```python
from xyz.gates import (
    Gate, QGateType, QBit, X, RY, CX,  # add whatever qcircuit actually uses
)
```

### 2i. `xyz/passes/mapping.py`

Replace line 6:

```python
from xyz.circuit import *
```

With explicit names. Same approach as 2h — grep for what the file references and list them.

- [ ] **Step 1: Apply each edit 2a–2i**

Read the current file, write the new content. Preserve docstrings and shebangs where present.

- [ ] **Step 2: Local regression**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `20 passed`.

If a test fails with `NameError` or `ImportError`, something was referenced implicitly through the old star import — add it to the explicit list in the offending module.

- [ ] **Step 3: State-suite regression** (catches more downstream name resolution issues)

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/ -v -m "not slow"
```

Expected: `50 passed`.

- [ ] **Step 4: Commit**

```bash
git add -u
git commit -m "refactor(exports): replace sub-package import * with explicit imports"
```

---

## Task 3: Pin `xyz/__init__.py` to the 9-symbol public API

**File:**
- Modify: `xyz/__init__.py`

Current content:

```python
from .synthesis import *
from .passes import *
from .utils import *
from .state import *
from .circuit import *
from .io import *
```

Replace entirely with:

```python
"""quantum-xyz — quantum circuit synthesis library.

Top-level public API. For anything not listed here, import from the
appropriate sub-package (xyz.gates, xyz.synthesis, xyz.passes,
xyz.io, xyz.state, xyz.utils)."""

from xyz.synthesis.prepare_state import (
    prepare_state,
    StatePreparationParameters,
)
from xyz.state.qstate import QState, quantize_state, D_state
from xyz.circuit.qcircuit import QCircuit
from xyz.io.simulate_circuit import simulate_circuit
from xyz.io.to_qiskit import to_qiskit
from xyz.utils.timer import stopwatch

__all__ = [
    "prepare_state",
    "QState",
    "QCircuit",
    "quantize_state",
    "simulate_circuit",
    "to_qiskit",
    "StatePreparationParameters",
    "stopwatch",
    "D_state",
]
```

- [ ] **Step 1: Apply the rewrite**

- [ ] **Step 2: Verify the pinned API resolves**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c "
import xyz
for name in ['prepare_state', 'QState', 'QCircuit', 'quantize_state',
             'simulate_circuit', 'to_qiskit', 'StatePreparationParameters',
             'stopwatch', 'D_state']:
    getattr(xyz, name)  # raises AttributeError if missing
    print(f'xyz.{name} ok')
"
```

Expected: 9 lines ending in `ok`.

- [ ] **Step 3: Verify NON-pinned names are NO LONGER exposed at top level**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c "
import xyz
for name in ['X', 'RY', 'MCRY', 'Gate', 'resynthesis', 'mapping']:
    try:
        getattr(xyz, name)
        print(f'STILL EXPOSED: xyz.{name}')
    except AttributeError:
        print(f'hidden: xyz.{name}')
"
```

Expected: 6 lines all starting with `hidden:`. If any print `STILL EXPOSED:`, the rewrite is leaking — investigate (probably a stray `from xyz.X import *` somewhere).

- [ ] **Step 4: Regression check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/ -v -m "not slow"
```

Expected: `50 passed`. Test files already use sub-package imports (`from xyz.gates.types import QBit` etc.) so they don't depend on top-level re-exports.

- [ ] **Step 5: Commit**

```bash
git add xyz/__init__.py
git commit -m "refactor(exports): pin xyz.* public API to 9 symbols"
```

---

## Task 4: Delete backwards-compat aliases accumulated through Phases 2–4

**Files to modify:**

- `xyz/gates/__init__.py` — delete the 5 legacy trait/gate aliases and their `__all__` entries
- `xyz/synthesis/prepare_state.py` — delete the `__Stats = Stats` alias

### 4a. `xyz/gates/__init__.py`

Find and delete these lines:

```python
# Backwards-compat legacy names (Phase 2 aliased these; external scripts
# may still import them).
QGate = Gate
UnitaryGate = UnitaryTrait
RotationGate = RotationTrait
ControlledGate = ControlledTrait
MultiControlledGate = MultiControlledTrait
```

Also remove these entries from the `__all__` list (both the comment line and the 5 alias names):

```python
    # legacy aliases
    "QGate",
    "UnitaryGate", "RotationGate", "ControlledGate", "MultiControlledGate",
```

### 4b. `xyz/synthesis/prepare_state.py`

Find and delete this line (near the top of the file, after the imports):

```python
# Backwards-compat alias — some tests still import the old name.
__Stats = Stats
```

- [ ] **Step 1: Apply both deletions**

- [ ] **Step 2: Regression check**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/ -v -m "not slow"
```

Expected: `50 passed`. If a test fails with `ImportError: cannot import name '__Stats'` or `cannot import name 'QGate'`, the test itself still references a legacy name — update that test to use the canonical name.

Candidate test files to check if regression fails:

```bash
grep -rn "__Stats\|QGate\|UnitaryGate\|RotationGate\|ControlledGate\|MultiControlledGate" tests/ | grep -v __pycache__
```

Update any hits: `__Stats` → `Stats`, `QGate` → `Gate`, etc.

- [ ] **Step 3: Commit**

```bash
git add -u
git commit -m "refactor(exports): delete Phase 2/4 backwards-compat aliases"
```

---

## Task 5: Verify no `import *` remains in `xyz/`

- [ ] **Step 1: Grep the source tree**

```bash
grep -rn "import \*" /home/hanyu/proj/quantum-xyz/xyz/ 2>/dev/null | grep -v __pycache__
```

Expected: **empty**. If any remain, they're fresh stars introduced by a subagent during Tasks 1–4 — rewrite them to explicit imports.

- [ ] **Step 2: Confirm `example/synthesize_dicke.py` still runs**

```bash
srun -p debug -A jcgroup --qos=low --time=5:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  example/synthesize_dicke.py 2>&1 | tail -10
```

Expected: runs to completion, writes `dicke.qasm`, no `ImportError`.

- [ ] **Step 3: Full regression + legacy tests on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=1:00:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  -u -m pytest tests/regression/ tests/test_algorithms/test_dicke.py \
  tests/test_algorithms/test_prepare_state.py -v --durations=10 \
  -m "not slow"
```

Expected: `56 passed, 1 deselected, 0 xfailed`.

- [ ] **Step 4: No commit (this task only verifies)**

---

## Task 6: Write exit record — refactor complete

- [ ] **Step 1: Write `docs/superpowers/plans/2026-04-21-phase5-exit.md`**

Content template:

```markdown
# Phase 5 Exit Record — Refactor Complete

All 5 refactor phases from `docs/superpowers/specs/2026-04-19-refactor-design.md` are done.

## Phase 5 what landed

- `__all__` declared on every leaf module under `xyz/`
- Every `from x import *` replaced with explicit named imports
- `xyz/__init__.py` pinned to 9 public symbols
- Phase 2/4 backwards-compat aliases deleted

## Public API (frozen)

```python
import xyz

xyz.prepare_state
xyz.QState
xyz.QCircuit
xyz.quantize_state
xyz.simulate_circuit
xyz.to_qiskit
xyz.StatePreparationParameters
xyz.stopwatch
xyz.D_state
```

Everything else imports from its sub-package: `from xyz.gates import X, CX`, `from xyz.synthesis import Stats`, etc.

## Suite state

Last slurm run, `-m "not slow"`:
`56 passed, 1 deselected, 0 xfailed`.

## Refactor summary across all 5 phases

| Phase | Deliverable |
|---|---|
| 0 | Regression safety net (50 fast tests + 1 slow) |
| 1 | 6 bug fixes; incidental 150x speedup for dense synthesis |
| 2 | Gate ABC + 9 missing apply() implementations + getter rename |
| 3 | `qgate.py` split into `xyz/gates/*` and `xyz/decomposition/*` |
| 4 | Strategy pattern for `prepare_state`; package reorg (synthesis / passes / io / state) |
| 5 | Explicit `__all__`; `from * import` eliminated; public API pinned |

The refactor reduced `xyz/circuit/qgate.py` from 858 lines to 0 (deleted), split across focused modules all under 200 lines. `_prepare_state_rec`'s 200-line body is now a `SynthesisEngine` + 4 strategy classes. Every gate honors the `Gate` ABC contract.
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/plans/2026-04-21-phase5-exit.md
git commit -m "docs: phase 5 exit record + refactor summary"
```

---

## Phase 5 exit criteria

- `grep -rn "import \*" xyz/` returns nothing.
- `python -c "import xyz; xyz.prepare_state"` works.
- `python -c "import xyz; xyz.X"` raises `AttributeError` (non-public names removed from top level).
- Every `__init__.py` under `xyz/` declares `__all__`.
- `56 passed, 1 deselected, 0 xfailed` on slurm.

## Out of Scope

- Documentation prose updates (README, sphinx docs). The spec's Phase 5 scope is the `__all__` sweep only.
- Publishing a new PyPI version. A follow-up release commit handles that.
- Renaming `tests/test_algorithms/` → `tests/test_synthesis/` to match the new package layout. Optional, not in Phase 5 scope.
