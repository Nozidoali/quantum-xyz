# Phase 1 — Bug Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Surgically fix six known bugs in `xyz/algorithms/initialization/prepare_state.py` and `xyz/circuit/qgate.py` without any refactor. Each fix gets a dedicated unit test that fails before the fix and passes after.

**Architecture:** All changes stay inside the current file layout. Tests live in a new `tests/regression/test_bug_fixes.py`. No API changes. The Phase 0 regression suite must stay green through every task.

**Tech Stack:** Python 3.10, pytest 8.2, numpy. Existing `xyz` package, poetry venv.

**Spec reference:** `docs/superpowers/specs/2026-04-19-refactor-design.md` — "Bug Fixes (Phase 1, pre-refactor)" section (6 items).

**Phase 0 exit record:** `docs/superpowers/plans/2026-04-19-phase0-exit.md`. Phase 0 is on `a9d0951`. Phase 1 commits land on top.

---

## File Structure

**New files:**
- `tests/regression/test_bug_fixes.py` — one test (or test group) per bug, all under 200 lines total

**Modified files:**
- `xyz/algorithms/initialization/prepare_state.py` — bugs 1, 2, 5, 6
- `xyz/circuit/qgate.py` — bugs 3 (Z.apply) and 4 (map_muxy typo)

---

## Ground rules for this phase

- **TDD per fix:** write the failing test first, confirm it fails on current code, then apply the minimal fix, confirm the test passes. One commit per (test + fix) pair. The commit message states which bug it closes.
- **Use the poetry venv python** for every pytest invocation:
  `/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest ...`
- **Keep tests cheap.** Use `num_qubits <= 3` trivial states. None of these tests call `xyz.prepare_state` on a large random dense state — a single cardinality-1 state is enough to exercise the control flow.
- **No scope creep.** Do not touch `pyproject.toml`, docs, or unrelated code.
- **Phase 0 guardrail:** after every bug-fix commit, run the regression suite (fast subset, `-m "not slow"`) on slurm to confirm no regression. Instructions for that appear in Task 7; between tasks 1-6 you may skip the full slurm run in favor of running just `tests/regression/test_bug_fixes.py` locally (cheap) and trust Task 7 as the cumulative check.

---

## Task 1: Bug 1 — mutable default `stats`

**Problem:** Both `prepare_state` and `_prepare_state_rec` declare `stats: __Stats = __Stats()` as their default argument. Python evaluates defaults once at function-definition time, so every call without an explicit `stats` shares the same `Stats` instance, and counters from one call leak into the next.

**Files:**
- Modify: `xyz/algorithms/initialization/prepare_state.py:88-93` (`_prepare_state_rec` signature)
- Modify: `xyz/algorithms/initialization/prepare_state.py:239-245` (`prepare_state` signature)
- Modify: `xyz/algorithms/initialization/prepare_state.py:290-301` (`prepare_state` body — initialize stats inside)
- Test: `tests/regression/test_bug_fixes.py` (new file)

- [ ] **Step 1: Write the failing test**

Create `tests/regression/test_bug_fixes.py` with:

```python
"""Unit tests that close specific bugs fixed in Phase 1 of the refactor.
Each test documents the bug it guards against in its docstring."""

from __future__ import annotations

import numpy as np
import pytest

import xyz
from xyz.algorithms.initialization.prepare_state import (
    StatePreparationParameters,
)


def _trivial_state(num_qubits: int = 3, index: int = 0) -> np.ndarray:
    """Cardinality-1 computational-basis state — cheap to synthesize."""
    vec = np.zeros(2**num_qubits)
    vec[index] = 1.0
    return vec


def test_prepare_state_default_stats_is_none():
    """Bug 1: `stats=Stats()` as a default argument is evaluated once at
    function-definition time, so every default-call shares the same
    instance. The fix makes the default a `None` sentinel; each call
    initializes its own Stats internally.

    Checking the signature directly is the clearest demonstration: a
    Stats instance default is the bug, None is the fix.
    """
    import inspect

    sig_outer = inspect.signature(xyz.prepare_state)
    outer_default = sig_outer.parameters["stats"].default
    assert outer_default is None, (
        f"prepare_state stats default is {type(outer_default).__name__}; "
        "expected None to avoid mutable-default sharing across calls"
    )

    from xyz.algorithms.initialization.prepare_state import _prepare_state_rec
    sig_inner = inspect.signature(_prepare_state_rec)
    inner_default = sig_inner.parameters["stats"].default
    assert inner_default is None, (
        f"_prepare_state_rec stats default is {type(inner_default).__name__}; "
        "expected None"
    )
```

Note: the module-level class `__Stats` has a double-underscore prefix but is not name-mangled at the module scope (name mangling only happens inside class bodies). It remains importable by that exact name, which matters later tasks use it.

- [ ] **Step 2: Run the test to confirm it fails on current code**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_prepare_state_default_stats_is_none -v
```

Expected: **FAIL** — the current default is a `__Stats` instance, so the assertion reports `prepare_state stats default is __Stats; expected None...`.

- [ ] **Step 3: Apply the fix**

In `xyz/algorithms/initialization/prepare_state.py`:

Replace the `_prepare_state_rec` signature (lines 88-93):

```python
def _prepare_state_rec(
    circuit: QCircuit,
    state: QState,
    verbose_level: int = 0,
    stats: "__Stats | None" = None,
    **kwargs,
):
    if stats is None:
        stats = __Stats()
```

Replace the `prepare_state` signature (lines 239-245):

```python
def prepare_state(
    state: QState,
    map_gates: bool = True,
    verbose_level: int = 0,
    param: StatePreparationParameters = None,
    stats: "__Stats | None" = None,
) -> QCircuit:
```

In the `prepare_state` body, initialize stats before the `_prepare_state_rec` call. Find:

```python
    # initialize a circuit and the quantum registers
    circuit = QCircuit(state.num_qubits, map_gates=map_gates)
```

Insert immediately above it:

```python
    if stats is None:
        stats = __Stats()
```

- [ ] **Step 4: Run the test to confirm it passes**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_prepare_state_default_stats_is_none -v
```

Expected: **PASS**.

- [ ] **Step 5: Commit**

```bash
git add tests/regression/test_bug_fixes.py xyz/algorithms/initialization/prepare_state.py
git commit -m "fix(prepare_state): replace mutable-default Stats with None sentinel"
```

---

## Task 2: Bug 2 — `param` dropped via `**kwargs`

**Problem:** `prepare_state` passes `param=param` to `_prepare_state_rec`. `_prepare_state_rec`'s signature only names `verbose_level`, `stats`, and `**kwargs`, so the incoming `param` enters `kwargs`. Inside the function, the first two lines overwrite `param` with a fresh `StatePreparationParameters()` and then call `param.update(**kwargs)`, which only accepts attributes that already exist on `StatePreparationParameters` (no `param` attribute, so the incoming object is silently discarded). Any caller-supplied `param` is ignored.

**Files:**
- Modify: `xyz/algorithms/initialization/prepare_state.py:88-104` (`_prepare_state_rec` — accept an explicit `param` parameter)
- Modify: `xyz/algorithms/initialization/prepare_state.py:175-180` and `199-204` (recursive self-calls — already pass `param=param`, keep that but confirm)
- Test: `tests/regression/test_bug_fixes.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/regression/test_bug_fixes.py`:

```python
def test_prepare_state_respects_explicit_param():
    """Bug 2: caller-supplied `param` is dropped inside `_prepare_state_rec`.

    If we pass a StatePreparationParameters that disables compression
    (support_reduction), the stats counter for support_reduction runs
    must reflect that, not the default-enabled behavior.
    """
    from xyz.algorithms.initialization.prepare_state import __Stats as Stats

    param = StatePreparationParameters()
    param.enable_compression = False
    param.enable_exact_synthesis = False
    param.enable_m_flow = False
    param.enable_n_flow = False

    stats = Stats()
    # A cardinality-1 state short-circuits on the trivial path before m/n-flow
    # are consulted, so disabling all methods is safe here — the assertion
    # exercises only the compression toggle.
    xyz.prepare_state(_trivial_state(), map_gates=True, param=param, stats=stats)

    # With enable_compression=False, support_reduction never runs.
    # Today (buggy) the param is discarded and compression runs anyway,
    # so this assertion fails.
    assert stats.time_support_reduction == 0, (
        f"expected support_reduction disabled, saw time_support_reduction="
        f"{stats.time_support_reduction}"
    )
```

- [ ] **Step 2: Run the test to confirm it fails**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_prepare_state_respects_explicit_param -v
```

Expected: **FAIL** — `stats.time_support_reduction > 0` because the bug discards `param`.

- [ ] **Step 3: Apply the fix**

In `xyz/algorithms/initialization/prepare_state.py`, replace the whole opening of `_prepare_state_rec` (lines 88-104). Currently:

```python
def _prepare_state_rec(
    circuit: QCircuit,
    state: QState,
    verbose_level: int = 0,
    stats: "__Stats | None" = None,
    **kwargs,
):
    if stats is None:
        stats = __Stats()
    prev_supports = state.get_supports()
    prev_num_supports = len(prev_supports)
    prev_density = state.get_sparsity()

    support_reducing_gates = []
    num_cx_support_reduction = 0

    # check the parameters
    param = StatePreparationParameters()
    param.update(**kwargs)
```

Replace with:

```python
def _prepare_state_rec(
    circuit: QCircuit,
    state: QState,
    verbose_level: int = 0,
    stats: "__Stats | None" = None,
    param: "StatePreparationParameters | None" = None,
):
    if stats is None:
        stats = __Stats()
    if param is None:
        param = StatePreparationParameters()

    prev_supports = state.get_supports()
    prev_num_supports = len(prev_supports)
    prev_density = state.get_sparsity()

    support_reducing_gates = []
    num_cx_support_reduction = 0
```

This removes the silent `**kwargs` path entirely. The two recursive self-calls at lines 175-180 and 199-204 already pass `param=param` as a named argument, so they need no changes — but verify them after the edit.

- [ ] **Step 4: Run both bug tests so far**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py -v
```

Expected: both `test_prepare_state_default_stats_not_shared` and
`test_prepare_state_respects_explicit_param` **PASS**.

- [ ] **Step 5: Commit**

```bash
git add tests/regression/test_bug_fixes.py xyz/algorithms/initialization/prepare_state.py
git commit -m "fix(prepare_state): pass param through as named arg, drop silent kwargs"
```

---

## Task 3: Bug 3 — `Z.apply` dead code + broken method

**Problem:** `Z.apply` in `xyz/circuit/qgate.py` builds an `index_to_weight` dict, then unconditionally raises `NotImplementedError`. The dict is dead code and the method is broken. Z is a phase-flip on the target qubit: `|...1...> → -|...1...>` on the bit at `target_qubit.index`, leaving `|...0...>` alone.

**Files:**
- Modify: `xyz/circuit/qgate.py:627-632`
- Test: `tests/regression/test_bug_fixes.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/regression/test_bug_fixes.py`:

```python
def test_Z_apply_flips_target_phase():
    """Bug 3: Z.apply populates a dict then raises unconditionally.

    Expected behavior: flip the sign of every amplitude whose target-qubit
    bit is 1. A basis state |01> on (q0=low, q1=high), with target=q0, is
    unchanged in magnitude but flipped in sign if the q0 bit is 1.
    """
    from xyz.circuit.qgate import QBit, Z

    # |01> in the xyz convention uses bit index = qubit index.
    # index 1 = binary 01 = q0 set, q1 clear.
    state = xyz.quantize_state(np.array([0.0, 1.0, 0.0, 0.0]))
    z0 = Z(QBit(0))
    out = z0.apply(state)
    vec = out.to_vector()
    assert np.allclose(vec, [0.0, -1.0, 0.0, 0.0]), f"got {vec}"

    # Z on a qubit whose bit is 0 for every nonzero amplitude → no sign flip.
    z1 = Z(QBit(1))
    out = z1.apply(state)
    vec = out.to_vector()
    assert np.allclose(vec, [0.0, 1.0, 0.0, 0.0]), f"got {vec}"
```

- [ ] **Step 2: Confirm it fails**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_Z_apply_flips_target_phase -v
```

Expected: **FAIL** with `NotImplementedError: Z gate not implemented`.

- [ ] **Step 3: Apply the fix**

In `xyz/circuit/qgate.py`, replace the whole `Z.apply` method (lines 627-632):

```python
    def apply(self, qstate: QState) -> QState:
        index_to_weight = {}
        for idx, weight in qstate.index_to_weight.items():
            if idx & (1 << self.target_qubit.index):
                index_to_weight[idx] = -weight
            else:
                index_to_weight[idx] = weight
        return QState(index_to_weight, qstate.num_qubits)
```

Two substantive differences vs. the old dead code:
- Iterate `qstate.index_to_weight.items()` rather than `qstate.index_set` (so we pick up weights, not just indices).
- Always assign (flipped or not) and return a new `QState` — no raise.

- [ ] **Step 4: Confirm it passes**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_Z_apply_flips_target_phase -v
```

Expected: **PASS**.

- [ ] **Step 5: Commit**

```bash
git add tests/regression/test_bug_fixes.py xyz/circuit/qgate.py
git commit -m "fix(qgate): implement Z.apply, remove dead dict-then-raise code"
```

---

## Task 4: Bug 4 — `map_muxy` uses non-existent `gate.type`

**Problem:** `map_muxy` (xyz/circuit/qgate.py:635) asserts `gate.type == QGateType.MULTIPLEX_Y`. `MULTIPLEXY` extends `AdvancedGate`, whose `__init__` sets `self.qgate_type` (not `self.type`). Any call to `map_muxy` raises `AttributeError` immediately. The call path in `QCircuit.add_gate` for `QGateType.MULTIPLEX_Y` is unreachable.

**Files:**
- Modify: `xyz/circuit/qgate.py:635-642`
- Test: `tests/regression/test_bug_fixes.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/regression/test_bug_fixes.py`:

```python
def test_map_muxy_does_not_raise_attribute_error():
    """Bug 4: `map_muxy` references gate.type which does not exist on
    MULTIPLEXY (the attribute is `qgate_type`). Today the call raises
    AttributeError before producing any gates.
    """
    from xyz.circuit.qgate import MULTIPLEXY, QBit, map_muxy

    gate = MULTIPLEXY(
        theta0=0.3,
        theta1=0.5,
        control_qubit=QBit(0),
        target_qubit=QBit(1),
    )
    mapped = map_muxy(gate)  # must not raise
    assert len(mapped) > 0, "map_muxy produced an empty gate list"
```

- [ ] **Step 2: Confirm it fails**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_map_muxy_does_not_raise_attribute_error -v
```

Expected: **FAIL** with `AttributeError: 'MULTIPLEXY' object has no attribute 'type'`.

- [ ] **Step 3: Apply the fix**

In `xyz/circuit/qgate.py`, change line 636 only:

From:
```python
    assert gate.type == QGateType.MULTIPLEX_Y
```

To:
```python
    assert gate.qgate_type == QGateType.MULTIPLEX_Y
```

Nothing else in `map_muxy` changes.

- [ ] **Step 4: Confirm it passes**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_map_muxy_does_not_raise_attribute_error -v
```

Expected: **PASS**.

- [ ] **Step 5: Commit**

```bash
git add tests/regression/test_bug_fixes.py xyz/circuit/qgate.py
git commit -m "fix(qgate): map_muxy — assert gate.qgate_type, not gate.type"
```

---

## Task 5: Bug 5 — `stats is not None` dead check

**Problem:** After the Task 1 fix, `stats` is guaranteed non-None by the time it is used inside `_prepare_state_rec` and `prepare_state`. Two `if stats is not None:` guards remain — one at line 154 in `_prepare_state_rec`, one at line 299 in `prepare_state`. They are always true. Remove them.

**Files:**
- Modify: `xyz/algorithms/initialization/prepare_state.py:154-155` (guard inside `_prepare_state_rec`)
- Modify: `xyz/algorithms/initialization/prepare_state.py:299-300` (guard inside `prepare_state`)
- Test: `tests/regression/test_bug_fixes.py`

The test here is a behavior-preserving one: passing `stats=None` to either function must still work (since Task 1's fix means the function initializes a Stats internally) and must not crash because of the removed guards.

- [ ] **Step 1: Add the failing test**

Append to `tests/regression/test_bug_fixes.py`:

```python
def test_prepare_state_with_stats_none_still_works():
    """Bug 5 companion: `stats is not None` guards inside prepare_state and
    _prepare_state_rec were dead after Task 1's fix. Removing them is
    behavior-preserving only if the functions correctly initialize stats
    when the caller passes None. This test pins that behavior.
    """
    circuit = xyz.prepare_state(_trivial_state(), map_gates=True, stats=None)
    # A cardinality-1 trivial state produces a valid circuit with 0 CNOTs.
    assert circuit.get_cnot_cost() == 0
```

- [ ] **Step 2: Confirm current state**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_prepare_state_with_stats_none_still_works -v
```

Expected: **PASS** (Task 1's fix already guarantees this works). This test exists to pin behavior so the Task 5 guard removal cannot regress it.

- [ ] **Step 3: Apply the fix**

Two surgical deletions in `xyz/algorithms/initialization/prepare_state.py`.

Inside `_prepare_state_rec`, find:

```python
            if stats is not None:
                stats.time_exact_cnot_synthesis += timer.time()
```

Replace with:

```python
            stats.time_exact_cnot_synthesis += timer.time()
```

Inside `prepare_state`, find:

```python
    if stats is not None:
        stats.time_total = timer.time()
```

Replace with:

```python
    stats.time_total = timer.time()
```

- [ ] **Step 4: Confirm the test still passes and no regression elsewhere**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py -v
```

Expected: all bug tests so far **PASS**.

- [ ] **Step 5: Commit**

```bash
git add tests/regression/test_bug_fixes.py xyz/algorithms/initialization/prepare_state.py
git commit -m "fix(prepare_state): drop dead `stats is not None` guards"
```

---

## Task 6: Bug 6 — `enable_reindex=True` raises after side effect

**Problem:** `_prepare_state_rec` has:

```python
    if param.enable_reindex:
        state, circuit = reindex_circuit(circuit, state)
        raise NotImplementedError("reindexing is not implemented yet")
```

The call to `reindex_circuit(circuit, state)` executes before the raise, mutating `circuit`/`state` before informing the caller that the feature is unimplemented. The fix: raise at the top of the branch, before any side effect.

**Files:**
- Modify: `xyz/algorithms/initialization/prepare_state.py:117-119`
- Test: `tests/regression/test_bug_fixes.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/regression/test_bug_fixes.py`:

```python
def test_enable_reindex_raises_before_side_effect():
    """Bug 6: enable_reindex=True path calls reindex_circuit(), then raises
    NotImplementedError unconditionally. The reindex call should NOT happen
    at all — the raise must come first.
    """
    param = StatePreparationParameters()
    param.enable_reindex = True

    # Patch reindex_circuit to record whether it was called. The fix means
    # NotImplementedError must be raised before the call site is reached.
    import xyz.algorithms.initialization.prepare_state as prepare_mod

    called = {"n": 0}
    original = prepare_mod.reindex_circuit

    def spy(*args, **kwargs):
        called["n"] += 1
        return original(*args, **kwargs)

    prepare_mod.reindex_circuit = spy
    try:
        with pytest.raises(NotImplementedError):
            xyz.prepare_state(_trivial_state(), map_gates=True, param=param)
    finally:
        prepare_mod.reindex_circuit = original

    assert called["n"] == 0, (
        f"reindex_circuit was called {called['n']} time(s) before the raise"
    )
```

- [ ] **Step 2: Confirm it fails**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py::test_enable_reindex_raises_before_side_effect -v
```

Expected: **FAIL** — `reindex_circuit` is called once before the raise, so `called["n"] == 1`.

- [ ] **Step 3: Apply the fix**

In `xyz/algorithms/initialization/prepare_state.py`, replace lines 117-119. Currently:

```python
    if param.enable_reindex:
        state, circuit = reindex_circuit(circuit, state)
        raise NotImplementedError("reindexing is not implemented yet")
```

Replace with:

```python
    if param.enable_reindex:
        raise NotImplementedError(
            "enable_reindex is not implemented; leave the flag at its default."
        )
```

(The `reindex_circuit` import higher in the file becomes unused but leave it — cleanup is not this task's scope.)

- [ ] **Step 4: Confirm it passes**

```bash
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py -v
```

Expected: all bug tests **PASS**.

- [ ] **Step 5: Commit**

```bash
git add tests/regression/test_bug_fixes.py xyz/algorithms/initialization/prepare_state.py
git commit -m "fix(prepare_state): enable_reindex raises before mutating state"
```

---

## Task 7: Full-suite regression verification on slurm

All six bug fixes are in. Verify the Phase 0 regression suite still passes and no bug-fix test was broken by a later task.

- [ ] **Step 1: Run local bug-fix tests**

```bash
cd /home/hanyu/proj/quantum-xyz
/home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python -m pytest \
  tests/regression/test_bug_fixes.py -v
```

Expected: 6 tests, all **PASS** (no xfail, no xpass, no fail).

- [ ] **Step 2: Run the full regression + legacy suite on slurm**

```bash
srun -p debug -A jcgroup --qos=low --time=1:00:00 -c 4 \
  --chdir=/home/hanyu/proj/quantum-xyz \
  /home/hanyu/.cache/pypoetry/virtualenvs/xyz-_j28njtQ-py3.10/bin/python \
  -m pytest tests/regression/ tests/test_algorithms/test_dicke.py \
  tests/test_algorithms/test_prepare_state.py -v --durations=10 \
  -m "not slow"
```

Expected summary: `47 passed, 1 deselected, 9 xfailed` (41 previous + 6 new bug tests = 47 PASS). Total runtime under 10 min.

If any previously-passing test now fails, identify which bug fix caused the regression. Likely candidates: Tasks 2 or 5 (they change `_prepare_state_rec` signature or internals). Revert the offending commit and re-examine the fix.

- [ ] **Step 3: Write the exit record**

Create `docs/superpowers/plans/2026-04-20-phase1-exit.md`:

```markdown
# Phase 1 Exit Record

All six bugs from the refactor spec are fixed. Each fix lands with a
unit test in `tests/regression/test_bug_fixes.py` that demonstrates the
pre-fix failure and the post-fix success.

## Bugs closed
1. Mutable-default `stats` in `prepare_state` and `_prepare_state_rec`
2. `param` silently dropped through `**kwargs`
3. `Z.apply` dead dict-then-raise
4. `map_muxy` asserting non-existent `gate.type`
5. Dead `stats is not None` guards (after Task 1's fix these are always
   true)
6. `enable_reindex=True` raising after a side-effect call

## Suite state

Last run on slurm (`a725155` base + Phase 1 commits):
`47 passed, 1 deselected, 9 xfailed` in under 10 minutes.

Phase 2 (Gate ABC + apply completion) may begin.
```

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-04-20-phase1-exit.md
git commit -m "docs: phase 1 exit record"
```

---

## Phase 1 exit criteria (for the record)

- `tests/regression/test_bug_fixes.py` has 6 passing tests, one per bug.
- `pytest tests/regression/ tests/test_algorithms/test_dicke.py tests/test_algorithms/test_prepare_state.py -m "not slow"` is green on slurm.
- No change to `pyproject.toml`, `tests/regression/builders.py`, or any file outside the two targets listed under "File Structure".
- Every commit message names the specific bug it closes.

## Out of Scope

- No ABC, no refactor — that's Phase 2.
- No cleanup of the now-unused `reindex_circuit` import — a later phase will sweep unused imports.
- No API rename — the `get_cnot_cost`/`get_qgate_type` getter renames are Phase 2.
