# Phase 4 — Strategy Pattern + Package Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the monolithic `_prepare_state_rec` function with a strategy-pattern engine (`SynthesisEngine` + 4 concrete strategies), and reorganize the top-level package layout so module names reflect concerns rather than the legacy `algorithms`/`circuit`/`external` split.

**Architecture:** Two orthogonal changes bundled in one phase. (A) The synthesis logic is refactored in place, then (B) the whole `algorithms/initialization/` tree moves to `synthesis/`, `algorithms/optimization/` to `passes/`, `external/` to `io/`, and `circuit/qstate.py` to `state/qstate.py`. (B) is a big-bang mv + import sweep.

**Tech Stack:** Python 3.10, pytest 8.2, numpy. No new external deps.

**Spec reference:** `docs/superpowers/specs/2026-04-19-refactor-design.md` — "Strategy Pattern for `prepare_state`" and "Phase 4 — Strategy Pattern and Package Reorganization" sections.

**Base commit:** Phase 3 exit at `ecdb88f`. Phase 4 lands on top.

---

## File Structure

### Part A — Strategy pattern (tasks 1–5, in-place under `xyz/algorithms/initialization/`)

**New files:**
- `xyz/algorithms/initialization/params.py` — `StatePreparationParameters` + `Stats` (moved out of `prepare_state.py`)
- `xyz/algorithms/initialization/strategies/__init__.py`
- `xyz/algorithms/initialization/strategies/base.py` — `SynthesisStrategy` ABC
- `xyz/algorithms/initialization/strategies/trivial.py` — cardinality==1 short-circuit
- `xyz/algorithms/initialization/strategies/exact_cnot.py` — exact CNOT synthesis wrapper
- `xyz/algorithms/initialization/strategies/m_flow.py` — cardinality reduction (was `sparse_state_synthesis.py` logic)
- `xyz/algorithms/initialization/strategies/n_flow.py` — qubit reduction (was `n_flow.py` logic)
- `xyz/algorithms/initialization/engine.py` — `SynthesisEngine`

**Modified:**
- `xyz/algorithms/initialization/prepare_state.py` — becomes a thin facade (~40 lines)

### Part B — Package reorganization (task 6, big-bang)

| Old path | New path |
|---|---|
| `xyz/algorithms/initialization/` | `xyz/synthesis/` |
| `xyz/algorithms/optimization/` | `xyz/passes/` |
| `xyz/external/` | `xyz/io/` |
| `xyz/circuit/qstate.py` | `xyz/state/qstate.py` (`xyz/state/__init__.py` created) |
| `xyz/algorithms/__init__.py` | deleted (empty package removed) |

`xyz/circuit/` keeps `qcircuit.py` + its `__init__.py`. The `__init__.py` re-exports from `xyz.state` and `xyz.gates` to preserve the legacy `from xyz.circuit import X, QState, QCircuit` surface.

---

## Ground rules

- **Strategy-first ordering.** Parts A (tasks 1–5) refactor in place. Part B (task 6) relocates. Verification runs after each.
- **Regression suite stays green.** Per-task: run `pytest tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py` locally (sub-second). Full slurm run is Task 8.
- **Poetry venv python** for everything: `/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python`.
- **No semantic changes.** Each strategy is extracted verbatim from the current `_prepare_state_rec` body; behavior must match. Post-task CNOT counts identical to Phase 3's.
- **Per-task focus.** Each subagent sees only the files it needs to touch. Subagents are not authorized to fix unrelated issues (if they find one, report it and leave it).

---

## Task 1: Move `StatePreparationParameters` and `Stats` to `params.py`

**Files:**
- Create: `xyz/algorithms/initialization/params.py`
- Modify: `xyz/algorithms/initialization/prepare_state.py` (delete the two class definitions; re-import from `params.py`)

- [ ] **Step 1: Write `xyz/algorithms/initialization/params.py`**

```python
"""Parameters and per-run statistics for state preparation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class StatePreparationParameters:
    EXACT_SYNTHESIS_DENSITY_THRESHOLD: int = 100
    EXACT_SYNTHESIS_CNOT_LIMIT: int = 100
    enable_exact_synthesis: bool = True
    enable_n_flow: bool = False
    enable_m_flow: bool = True
    enable_decomposition: bool = False
    enable_compression: bool = True
    enable_reindex: bool = False
    n_qubits_max: int = 5

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Stats:
    """Per-run counters for a state-preparation call."""

    time_total: float = 0.0
    num_runs_support_reduction: int = 0
    num_reduced_supports: int = 0
    num_reduced_density: int = 0
    num_saved_gates_decision: int = 0
    num_methods: Optional[Dict[str, int]] = None

    time_support_reduction: float = 0.0
    time_exact_cnot_synthesis: float = 0.0
    time_cardinality_reduction: float = 0.0
    time_qubit_decomposition: float = 0.0

    def __post_init__(self):
        if self.num_methods is None:
            self.num_methods = {}

    def report(self) -> None:
        print("-" * 80)
        print(f"time_total: {self.time_total}")
        print("-" * 80)
        print(f"num_runs_support_reduction: {self.num_runs_support_reduction}")
        print(f"time_support_reduction: {self.time_support_reduction:0.02f} sec")
        print(f"time_exact_cnot_synthesis: {self.time_exact_cnot_synthesis:0.02f} sec")
        print(
            f"time_cardinality_reduction: {self.time_cardinality_reduction:0.02f} sec"
        )
        print(f"time_qubit_decomposition: {self.time_qubit_decomposition:0.02f} sec")
        print(f"num_reduced_supports: {self.num_reduced_supports}")
        print(f"num_reduced_density: {self.num_reduced_density}")
        print(f"num_saved_gates_decision: {self.num_saved_gates_decision}")
        print("-" * 80)
        for method, num in self.num_methods.items():
            print(f"{method}: {num}")
        print("-" * 80)
```

Note the rename from the double-underscore `__Stats` to plain `Stats` — the double-underscore was name-mangling spuriously (Phase 0 spec called this out). The old name will be kept as an alias so existing callers still resolve (step 3 handles it).

- [ ] **Step 2: Update `xyz/algorithms/initialization/prepare_state.py`**

Find the two class definitions (`@dataclass class StatePreparationParameters` and `@dataclass class __Stats`) at the top of the file. Delete them.

Replace with:

```python
from xyz.algorithms.initialization.params import (
    StatePreparationParameters,
    Stats,
)

# Backwards-compat alias for the old double-underscore name used inside
# this module. Phase 5 drops the alias when the import-sweep cleans up.
__Stats = Stats
```

- [ ] **Step 3: Regression check**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `20 passed`.

- [ ] **Step 4: Commit**

```bash
git add xyz/algorithms/initialization/params.py xyz/algorithms/initialization/prepare_state.py
git commit -m "refactor(synthesis): extract StatePreparationParameters/Stats to params.py"
```

---

## Task 2: `strategies/base.py` — `SynthesisStrategy` ABC

**Files:**
- Create: `xyz/algorithms/initialization/strategies/__init__.py`
- Create: `xyz/algorithms/initialization/strategies/base.py`

- [ ] **Step 1: Create the package marker**

```bash
: > xyz/algorithms/initialization/strategies/__init__.py
```

- [ ] **Step 2: Write `xyz/algorithms/initialization/strategies/base.py`**

```python
"""SynthesisStrategy ABC.

Each strategy knows how to synthesize a target QState into a list of
gates and reports its CNOT cost. Strategies hold a back-reference to
the engine so they can recurse on sub-states."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from xyz.circuit import QCircuit
    from xyz.circuit.qstate import QState
    from xyz.gates.base import Gate
    from xyz.algorithms.initialization.engine import SynthesisEngine
    from xyz.algorithms.initialization.params import (
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
```

- [ ] **Step 3: Regression check** (just import, no tests touch this yet)

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c \
  "from xyz.algorithms.initialization.strategies.base import SynthesisStrategy; print('ok')"
```

Expected: `ok`.

- [ ] **Step 4: Commit**

```bash
git add xyz/algorithms/initialization/strategies/__init__.py xyz/algorithms/initialization/strategies/base.py
git commit -m "refactor(synthesis): add SynthesisStrategy ABC"
```

---

## Task 3: `TrivialStrategy` + `ExactCNOTStrategy` (short-circuit strategies)

**Files:**
- Create: `xyz/algorithms/initialization/strategies/trivial.py`
- Create: `xyz/algorithms/initialization/strategies/exact_cnot.py`

These two strategies **short-circuit** — when applicable they produce the final answer without delegating to m-flow/n-flow. The engine uses them first; the others are fallback.

- [ ] **Step 1: Write `trivial.py`**

```python
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
```

- [ ] **Step 2: Write `exact_cnot.py`**

```python
"""Exact CNOT synthesis — used when the target fits the threshold.
Wraps the existing `exact_cnot_synthesis` function."""

from __future__ import annotations

from xyz.algorithms.initialization.exact_cnot_synthesis import (
    exact_cnot_synthesis,
)
from xyz.algorithms.initialization.strategies.base import SynthesisStrategy
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
```

- [ ] **Step 3: Import check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c \
  "from xyz.algorithms.initialization.strategies.trivial import TrivialStrategy;
   from xyz.algorithms.initialization.strategies.exact_cnot import ExactCNOTStrategy;
   print('ok')"
```

Expected: `ok`.

- [ ] **Step 4: Commit**

```bash
git add xyz/algorithms/initialization/strategies/trivial.py xyz/algorithms/initialization/strategies/exact_cnot.py
git commit -m "refactor(synthesis): add TrivialStrategy and ExactCNOTStrategy"
```

---

## Task 4: `MFlowStrategy` + `NFlowStrategy` (competing strategies)

These two strategies both call back into `self.engine.run(...)` to recurse on a smaller sub-state.

- [ ] **Step 1: Write `m_flow.py`**

```python
"""Cardinality-reduction strategy (m-flow).

Reduces the state's cardinality by one via cardinality_reduction, then
recurses on the smaller state through the engine."""

from __future__ import annotations

from xyz.algorithms.initialization.sparse_state_synthesis import (
    cardinality_reduction,
)
from xyz.algorithms.initialization.strategies.base import SynthesisStrategy
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
```

- [ ] **Step 2: Write `n_flow.py`**

```python
"""Qubit-reduction strategy (n-flow).

Reduces the qubit count by one via qubit_reduction, then recurses."""

from __future__ import annotations

from xyz.algorithms.initialization.n_flow import qubit_reduction
from xyz.algorithms.initialization.strategies.base import SynthesisStrategy
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
```

- [ ] **Step 3: Import check**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -c \
  "from xyz.algorithms.initialization.strategies.m_flow import MFlowStrategy;
   from xyz.algorithms.initialization.strategies.n_flow import NFlowStrategy;
   print('ok')"
```

Expected: `ok`.

- [ ] **Step 4: Commit**

```bash
git add xyz/algorithms/initialization/strategies/m_flow.py xyz/algorithms/initialization/strategies/n_flow.py
git commit -m "refactor(synthesis): add MFlowStrategy and NFlowStrategy"
```

---

## Task 5: `SynthesisEngine` + `prepare_state` facade

**Files:**
- Create: `xyz/algorithms/initialization/engine.py`
- Modify: `xyz/algorithms/initialization/prepare_state.py` (replace `_prepare_state_rec` body with engine instantiation)

- [ ] **Step 1: Write `engine.py`**

```python
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
```

- [ ] **Step 2: Rewrite `xyz/algorithms/initialization/prepare_state.py`** as a thin facade

Replace the entire file with:

```python
"""Thin facade over SynthesisEngine.

Reference:
    @article{wang2024quantum,
        title={Quantum State Preparation Using an Exact CNOT Synthesis Formulation},
        author={Wang, Hanyu and Tan, Bochen and Cong, Jason and De Micheli, Giovanni},
        journal={arXiv preprint arXiv:2401.01009},
        year={2024}
    }
"""

from __future__ import annotations

from typing import Optional, Union

import numpy as np

from xyz.circuit import QCircuit, QState, quantize_state
from xyz.algorithms.initialization.engine import SynthesisEngine
from xyz.algorithms.initialization.params import (
    StatePreparationParameters,
    Stats,
)
from xyz.utils import global_stopwatch_report, stopwatch

# Backwards-compat alias — some tests still import the old name.
__Stats = Stats


def prepare_state(
    state: Union[QState, np.ndarray],
    map_gates: bool = True,
    verbose_level: int = 0,
    param: Optional[StatePreparationParameters] = None,
    stats: Optional[Stats] = None,
) -> QCircuit:
    """Prepare the target state by synthesizing a quantum circuit.

    :param state: target QState or a real-amplitude np.ndarray.
    :param map_gates: map the resulting circuit to {U2, CX} primitives.
    :param param: synthesis parameters; if None, a sparse/dense heuristic
        picks reasonable defaults.
    :param stats: per-run counters; one is created if not given.
    """

    if not isinstance(state, QState):
        if isinstance(state, np.ndarray):
            state = quantize_state(state)
        else:
            raise ValueError("state must be either a QState or a numpy array")

    if param is None:
        # Sparse states prefer m-flow; dense states prefer n-flow.
        num_qubits = state.num_qubits
        cardinality = state.get_sparsity()
        m_cost = int(cardinality * num_qubits)
        n_cost = 1 << num_qubits
        param = StatePreparationParameters()
        if m_cost < n_cost:
            param.enable_m_flow = True
            param.enable_n_flow = False
        else:
            param.enable_m_flow = False
            param.enable_n_flow = True

    if stats is None:
        stats = Stats()

    circuit = QCircuit(state.num_qubits, map_gates=map_gates)
    engine = SynthesisEngine(param, stats, verbose_level)

    with stopwatch("prepare_state") as timer:
        gates, _ = engine.run(circuit, state)

    stats.time_total = timer.time()
    circuit.add_gates(gates)

    if verbose_level >= 1:
        global_stopwatch_report()
    return circuit
```

Delete the old `_prepare_state_rec` function, the `@dataclass class __Stats` definition, and the `@dataclass class StatePreparationParameters` definition (already moved in Task 1, but verify no stragglers).

- [ ] **Step 3: Local regression**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py tests/regression/test_gate_apply.py -v
```

Expected: `20 passed`. The bug-fix tests exercise `prepare_state` with trivial states (cardinality=1) — they short-circuit via `TrivialStrategy`.

- [ ] **Step 4: State-suite regression** (exercises m-flow + n-flow paths)

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_dense_states.py \
  tests/regression/test_sparse_states.py \
  tests/regression/test_dicke_states.py -v
```

Expected: `30 passed`. If a test fails with a CNOT-bound violation, the engine's flow selection drifted — inspect the failing case and compare Phase 3's golden bounds in `tests/regression/golden_bounds.json` against the actual count.

- [ ] **Step 5: Commit**

```bash
git add xyz/algorithms/initialization/engine.py xyz/algorithms/initialization/prepare_state.py
git commit -m "refactor(synthesis): wire SynthesisEngine + prepare_state facade"
```

---

## Task 6: Package reorganization (big-bang mv + import sweep)

This is the largest task in Phase 4. Done in one commit so `git log` shows the rename, not a pile of intermediate half-moved states.

**Moves:**

| Old | New |
|---|---|
| `xyz/algorithms/initialization/` | `xyz/synthesis/` |
| `xyz/algorithms/optimization/` | `xyz/passes/` |
| `xyz/external/` | `xyz/io/` |
| `xyz/circuit/qstate.py` | `xyz/state/qstate.py` |

Also: `xyz/algorithms/` becomes an empty directory and gets removed. `xyz/state/__init__.py` is created (re-exports from `qstate`).

- [ ] **Step 1: Move the directory trees with `git mv`** (keeps file history)

```bash
cd /home/hanyu/proj/quantum-xyz
mkdir -p xyz/state
git mv xyz/algorithms/initialization xyz/synthesis
git mv xyz/algorithms/optimization xyz/passes
git mv xyz/external xyz/io
git mv xyz/circuit/qstate.py xyz/state/qstate.py
# remove the now-empty algorithms/__init__.py (if present) and the directory
git rm xyz/algorithms/__init__.py 2>/dev/null || true
rmdir xyz/algorithms 2>/dev/null || true
```

- [ ] **Step 2: Create the new `xyz/state/__init__.py`**

```python
"""Quantum state data types."""

from xyz.state.qstate import *  # noqa: F401,F403
```

- [ ] **Step 3: Rename the former package name in `xyz/synthesis/`'s internal imports**

Every file under `xyz/synthesis/` that has `from xyz.algorithms.initialization...` or `from xyz.algorithms.initialization.<x> import ...` needs its import path updated. Sweep:

```bash
grep -rln "xyz\.algorithms\.initialization\|xyz\.algorithms\.optimization\|xyz\.external" xyz tests example | grep -v __pycache__
```

For each file: replace

- `xyz.algorithms.initialization` → `xyz.synthesis`
- `xyz.algorithms.optimization` → `xyz.passes`
- `xyz.external` → `xyz.io`

**sed one-liner:**

```bash
FILES=$(grep -rln "xyz\.algorithms\.initialization\|xyz\.algorithms\.optimization\|xyz\.external" xyz tests example | grep -v __pycache__)
for f in $FILES; do
  sed -i 's|xyz\.algorithms\.initialization|xyz.synthesis|g' "$f"
  sed -i 's|xyz\.algorithms\.optimization|xyz.passes|g' "$f"
  sed -i 's|xyz\.external|xyz.io|g' "$f"
done
```

- [ ] **Step 4: Relative-import fixes**

Within `xyz/synthesis/`, `xyz/passes/`, and `xyz/io/`, internal `from .xxx import` relative imports stay as-is (relative imports don't care about package location).

BUT — some files use `from ..<sibling_package>.<module>` notation (e.g. `from xyz.synthesis.support_reduction import ...` already absolute after Step 3 — fine). If a file has `from ..optimization.mapping import ...`, change it to `from xyz.passes.mapping import ...` to use the new package name.

Scan:

```bash
grep -rn "from \.\.optimization\|from \.\.external\|from \.\.algorithms" xyz | grep -v __pycache__
```

Fix each by hand using the mapping above. Most likely zero hits if callers used absolute paths.

- [ ] **Step 5: Sweep `xyz/circuit/__init__.py` and `xyz/circuit/qcircuit.py`**

`xyz/circuit/__init__.py` currently has `from .qstate import *`. `qstate.py` moved to `xyz/state/qstate.py`. Change:

```python
from .qstate import *
```

to:

```python
from xyz.state.qstate import *
```

Also `xyz/circuit/qcircuit.py` probably has `from .qstate import QState`. Change to:

```python
from xyz.state.qstate import QState
```

- [ ] **Step 6: Sweep `xyz/__init__.py`**

Currently:

```python
from .algorithms import *
from .utils import *
from .circuit import *
from .external import *
```

Update to:

```python
from .synthesis import *
from .passes import *
from .utils import *
from .circuit import *
from .state import *
from .io import *
```

(Order matters for re-export precedence but practically we want `circuit` + `state` present; put `synthesis` first since it imports from gates/state/circuit transitively.)

- [ ] **Step 7: Delete the old `xyz/algorithms/` `__init__.py` if `rmdir` in Step 1 didn't catch it**

```bash
find xyz/algorithms -type d -empty -delete 2>/dev/null || true
```

- [ ] **Step 8: Verify no stale references**

```bash
grep -rln "xyz\.algorithms\|xyz\.external\|xyz/circuit/qstate\|from .qstate\|\.external\." xyz tests example 2>/dev/null | grep -v __pycache__ | grep -v docs/
```

Expected: empty or only documentation references. Any hits in `xyz/`, `tests/`, or `example/` indicate something the sweep missed — fix them individually.

- [ ] **Step 9: Full regression (local)**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/ -v -m "not slow"
```

Expected: `50 passed, 0 xfailed`.

- [ ] **Step 10: Legacy tests**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/test_algorithms/ tests/test_circuit/ -v -m "not slow"
```

Expected: no new failures. Some of these tests may already have been broken pre-Phase-4 (they're not in the regression safety net); accept that as unchanged.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
refactor(layout): algorithms/{initialization,optimization} → synthesis/, passes/

Also moves:
- xyz/external/ → xyz/io/
- xyz/circuit/qstate.py → xyz/state/qstate.py

Updates all absolute imports via sed sweep. Relative imports unchanged
(they don't reference package paths). xyz/__init__.py re-exports from
the new package names so `from xyz import prepare_state, QState`
continues to work.
EOF
)"
```

---

## Task 7: Verify `example/` scripts run

The examples exercise the library via the public surface; a successful run confirms the reorg didn't break downstream callers.

- [ ] **Step 1: Run `synthesize_dicke.py` on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=5:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  example/synthesize_dicke.py 2>&1 | tail -20
```

Expected: runs to completion (nonzero stdout is fine), no `ImportError` or `ModuleNotFoundError`.

- [ ] **Step 2: Run `resynthesize_circuit.py` on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=5:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  example/resynthesize_circuit.py 2>&1 | tail -20
```

Expected: runs to completion.

- [ ] **Step 3: Run `run_simulation.py` on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=5:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  example/run_simulation.py 2>&1 | tail -20
```

Expected: runs to completion.

- [ ] **Step 4: If any example fails with `ImportError`, fix its imports**

The failure message names the module. Update the import to use the new paths per the mapping table in Task 6. Example:

```python
# Before
from xyz.external import simulate_circuit
# After
from xyz.io import simulate_circuit
```

Re-run Step 1–3 after fixes until all three pass.

- [ ] **Step 5: Commit any example fixes**

```bash
git add example/
git commit -m "example: update imports for Phase 4 package reorg"
# or if nothing changed, skip this commit
```

---

## Task 8: Full-suite slurm verification + exit record

- [ ] **Step 1: Run the full regression + legacy suite on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=1:00:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  -u -m pytest tests/regression/ tests/test_algorithms/test_dicke.py \
  tests/test_algorithms/test_prepare_state.py -v --durations=10 \
  -m "not slow"
```

Expected: `56 passed, 1 deselected, 0 xfailed`. Same as Phase 3 — the refactor preserves semantics.

If any test fails, it's a sweep miss from Task 6 — grep the failing import and fix.

- [ ] **Step 2: Write the exit record**

Create `docs/superpowers/plans/2026-04-20-phase4-exit.md`:

```markdown
# Phase 4 Exit Record

Strategy pattern replaces `_prepare_state_rec`. Package layout reflects
concerns (`synthesis/`, `passes/`, `io/`, `state/`) rather than the
legacy `algorithms`/`circuit`/`external` split.

## What landed

- `xyz/synthesis/params.py` — `StatePreparationParameters`, `Stats`
- `xyz/synthesis/strategies/base.py` — `SynthesisStrategy` ABC
- `xyz/synthesis/strategies/{trivial,exact_cnot,m_flow,n_flow}.py`
- `xyz/synthesis/engine.py` — `SynthesisEngine`
- `xyz/synthesis/prepare_state.py` — thin facade (~50 lines)
- Package moves:
  - `xyz/algorithms/initialization/` → `xyz/synthesis/`
  - `xyz/algorithms/optimization/` → `xyz/passes/`
  - `xyz/external/` → `xyz/io/`
  - `xyz/circuit/qstate.py` → `xyz/state/qstate.py`

## Suite state

Last slurm run, `-m "not slow"`:
`56 passed, 1 deselected, 0 xfailed`.

`example/synthesize_dicke.py`, `example/resynthesize_circuit.py`, and
`example/run_simulation.py` all run end-to-end.

## Design notes

- The engine's three-phase pipeline matches the pre-refactor
  `_prepare_state_rec`: support reduction → short-circuit strategies
  (Trivial, ExactCNOT) → competing strategies (MFlow, NFlow).
- `SynthesisStrategy.applicable` is cheap; `.synthesize` does the work.
  Strategies hold `self.engine` to recurse on sub-states.
- The short-circuit / competing distinction lives in
  `SynthesisEngine.run`, not in strategy code — strategies are unaware
  of their scheduling category.
- `Stats`'s old name `__Stats` (double-underscore) was an accidental
  class-body name-mangling trap. Phase 4's params.py uses plain `Stats`;
  a `__Stats = Stats` alias keeps legacy imports working.

Phase 5 (`import *` cleanup + explicit `__all__`) may begin.
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-20-phase4-exit.md
git commit -m "docs: phase 4 exit record"
```

---

## Phase 4 exit criteria

- `xyz/synthesis/`, `xyz/passes/`, `xyz/io/`, `xyz/state/` exist.
- `xyz/algorithms/` does not exist.
- `xyz/circuit/qstate.py` does not exist.
- `_prepare_state_rec` does not exist; `SynthesisEngine` + 4 strategies replace it.
- `xyz/synthesis/prepare_state.py` is under 80 lines.
- `grep -rn "xyz.algorithms\|xyz.external" xyz tests example` is empty (ignoring `docs/`).
- `56 passed, 1 deselected, 0 xfailed` on slurm.
- All 3 `example/` top-level scripts run end-to-end.

## Out of Scope

- `import *` cleanup — Phase 5.
- Explicit `__all__` in every `__init__.py` — Phase 5.
- Top-level API freeze (`xyz.prepare_state`, `xyz.QState`, etc. as the only supported surface) — Phase 5.
