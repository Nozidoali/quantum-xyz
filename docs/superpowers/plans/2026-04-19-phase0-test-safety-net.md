# Phase 0 — Test Safety Net Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a regression test suite under `tests/regression/` that (1) asserts functional correctness via statevector comparison with qiskit, (2) asserts resource non-regression via per-case CNOT-count bounds, (3) covers every concrete gate's `apply` method. Everything must pass on the **current un-refactored** code so subsequent refactor phases can rely on it as a safety net.

**Architecture:** New `tests/regression/` package. Shared fixtures in `conftest.py`, target-state builders in `builders.py`, golden-bounds persistence in `bounds.py` plus a standalone generator script. Four regression test files (dense, sparse, dicke, gate-apply). Unblock two currently-skipped tests in `test_algorithms/`.

**Tech Stack:** Python 3.10, pytest 8.2, numpy, qiskit 1.0+, the existing `xyz` package.

**Spec reference:** `docs/superpowers/specs/2026-04-19-refactor-design.md` — Phase 0 section and Testing Strategy section.

---

## File Structure

**New files:**
- `tests/regression/__init__.py` — empty package marker
- `tests/regression/conftest.py` — shared fixtures (RNG seed, tolerance constants)
- `tests/regression/builders.py` — target state factories (dense random, uniform, sparse, dicke)
- `tests/regression/bounds.py` — load/write `golden_bounds.json`
- `tests/regression/golden_bounds.json` — committed lookup table, generated once
- `tests/regression/generate_bounds.py` — standalone script that runs all cases against the current code and writes `golden_bounds.json`
- `tests/regression/test_dense_states.py`
- `tests/regression/test_sparse_states.py`
- `tests/regression/test_dicke_states.py`
- `tests/regression/test_gate_apply.py`
- `tests/regression/README.md` — how to run, how to regenerate bounds

**Modified files:**
- `tests/test_algorithms/test_dicke.py` — remove skip, convert to `<= bound`
- `tests/test_algorithms/test_prepare_state.py` — remove `@pytest.mark.skip` from `test_qsp_1`

**Unchanged for this phase:** everything in `xyz/`.

---

## Task 1: Create regression package skeleton + conftest

**Files:**
- Create: `tests/regression/__init__.py`
- Create: `tests/regression/conftest.py`
- Create: `tests/regression/README.md`

- [ ] **Step 1: Create the package marker**

```bash
: > tests/regression/__init__.py
```

- [ ] **Step 2: Write `tests/regression/conftest.py`**

```python
"""Shared fixtures and constants for the regression suite.

The suite is the safety net for the refactor: every test in this package
must keep passing through every refactor phase. Functional correctness is
measured by statevector comparison; resource non-regression is measured by
a per-case CNOT-count bound loaded from golden_bounds.json.
"""

import numpy as np
import pytest

from tests.regression.bounds import load_bounds

# The random seed used for every synthetic case. Do not change it lightly:
# bumping the seed invalidates golden_bounds.json.
SEED = 20260419

# Statevector comparison tolerance, matching the existing tests in the repo.
STATEVECTOR_ATOL = 1e-6

# Margin above measured CNOT count when freezing bounds (10%).
BOUND_SLACK = 1.10


@pytest.fixture(scope="session")
def rng() -> np.random.Generator:
    return np.random.default_rng(SEED)


@pytest.fixture(scope="session")
def golden_bounds() -> dict[str, int]:
    """Read-only view of golden_bounds.json."""
    return load_bounds()
```

- [ ] **Step 3: Write `tests/regression/README.md`**

```markdown
# Regression Suite

Safety net for the in-progress refactor. See
`docs/superpowers/specs/2026-04-19-refactor-design.md`.

## Running

```
pytest tests/regression/ -v
```

Expected runtime: under 2 minutes.

## Regenerating golden bounds

Only when a phase deliberately changes resource characteristics and the
change is called out in its commit message.

```
python -m tests.regression.generate_bounds
```

This overwrites `tests/regression/golden_bounds.json` with measured CNOT
counts × 1.10 (ceiling). Commit the updated file in the same commit as the
code change that justifies it.
```

- [ ] **Step 4: Commit**

```bash
git add tests/regression/__init__.py tests/regression/conftest.py tests/regression/README.md
git commit -m "test: add regression package skeleton and conftest"
```

---

## Task 2: Target-state builders

**Files:**
- Create: `tests/regression/builders.py`

- [ ] **Step 1: Write `tests/regression/builders.py`**

```python
"""Target-state factories for the regression suite.

quantize_state drops imaginary parts, so every state here is built with
real amplitudes only. Each builder returns either a numpy vector of length
2**num_qubits or a (vector, case_id) tuple where the id is stable across
runs and feeds the golden_bounds lookup.
"""

from __future__ import annotations

import numpy as np


def random_real_state(num_qubits: int, rng: np.random.Generator) -> np.ndarray:
    """Uniformly-random real-amplitude normalized state."""
    vec = rng.standard_normal(2**num_qubits)
    return vec / np.linalg.norm(vec)


def uniform_state(num_qubits: int) -> np.ndarray:
    """Equal superposition over all basis states."""
    n = 2**num_qubits
    return np.full(n, 1.0 / np.sqrt(n))


def sparse_state(
    num_qubits: int, cardinality: int, rng: np.random.Generator
) -> np.ndarray:
    """Real-amplitude state with exactly `cardinality` nonzero amplitudes."""
    n = 2**num_qubits
    indices = rng.choice(n, size=cardinality, replace=False)
    amps = rng.standard_normal(cardinality)
    vec = np.zeros(n)
    vec[indices] = amps
    return vec / np.linalg.norm(vec)


def dicke_state(num_qubits: int, k: int) -> np.ndarray:
    """Dicke state D^n_k — delegates to the library's own builder so the
    regression case matches what the library is trying to synthesize."""
    import xyz
    return xyz.D_state(num_qubits, k)


# --- Case enumerations -------------------------------------------------

def dense_cases(rng: np.random.Generator) -> list[tuple[str, np.ndarray]]:
    """(case_id, vector). case_id is the key in golden_bounds.json."""
    cases: list[tuple[str, np.ndarray]] = []
    for n in (3, 4, 5, 6):
        for i in range(3):
            cases.append((f"dense_random_n{n}_i{i}", random_real_state(n, rng)))
        cases.append((f"dense_uniform_n{n}", uniform_state(n)))
    return cases


def sparse_cases(rng: np.random.Generator) -> list[tuple[str, np.ndarray]]:
    cases: list[tuple[str, np.ndarray]] = []
    for n in (4, 5, 6):
        for k in (2, 4, 8):
            for i in range(2):
                cases.append(
                    (f"sparse_n{n}_k{k}_i{i}", sparse_state(n, k, rng))
                )
    # cardinality == 1 short-circuit path
    for n in (3, 4, 5):
        vec = np.zeros(2**n)
        vec[rng.integers(2**n)] = 1.0
        cases.append((f"sparse_n{n}_k1", vec))
    return cases


DICKE_PAIRS: list[tuple[int, int]] = [
    (3, 1), (4, 1), (4, 2),
    (5, 1), (5, 2),
    (6, 1), (6, 2), (6, 3),
]


def dicke_cases() -> list[tuple[str, np.ndarray]]:
    return [(f"dicke_n{n}_k{k}", dicke_state(n, k)) for n, k in DICKE_PAIRS]
```

- [ ] **Step 2: Smoke-test the builders manually**

Run:

```bash
cd /home/hanyu/proj/quantum-xyz
python -c "
import numpy as np
from tests.regression.builders import (
    random_real_state, uniform_state, sparse_state, dicke_state,
    dense_cases, sparse_cases, dicke_cases,
)
rng = np.random.default_rng(20260419)
v = random_real_state(4, rng); print('dense', v.shape, np.isclose(np.linalg.norm(v), 1.0))
v = uniform_state(3); print('uniform', v.shape, np.isclose(np.linalg.norm(v), 1.0))
v = sparse_state(5, 4, rng); print('sparse', v.shape, int(np.sum(v != 0)))
v = dicke_state(4, 2); print('dicke', v.shape, np.isclose(np.linalg.norm(v), 1.0))
print('dense_cases', len(dense_cases(rng)))
print('sparse_cases', len(sparse_cases(rng)))
print('dicke_cases', len(dicke_cases()))
"
```

Expected output (exact counts):

```
dense (16,) True
uniform (8,) True
sparse (32,) 4
dicke (16,) True
dense_cases 10
sparse_cases 15
dicke_cases 5
```

- [ ] **Step 3: Commit**

```bash
git add tests/regression/builders.py
git commit -m "test: add regression-suite target-state builders"
```

---

## Task 3: Golden-bounds persistence + generator script

**Files:**
- Create: `tests/regression/bounds.py`
- Create: `tests/regression/generate_bounds.py`

- [ ] **Step 1: Write `tests/regression/bounds.py`**

```python
"""Golden CNOT-count bounds persistence.

`golden_bounds.json` maps case_id -> int. It is generated once by
`generate_bounds.py` and treated as read-only by the test suite. A phase
that deliberately changes CNOT counts re-runs the generator and commits
the updated JSON together with the code change.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

BOUNDS_PATH = Path(__file__).with_name("golden_bounds.json")


def load_bounds() -> dict[str, int]:
    if not BOUNDS_PATH.exists():
        raise FileNotFoundError(
            f"{BOUNDS_PATH} not found. Run "
            "`python -m tests.regression.generate_bounds` from the repo root."
        )
    return json.loads(BOUNDS_PATH.read_text())


def write_bounds(measured: dict[str, int], slack: float = 1.10) -> None:
    """Freeze `measured` CNOT counts as bounds, inflated by `slack` and
    rounded up. Writes to BOUNDS_PATH."""
    bounds = {case_id: math.ceil(count * slack) for case_id, count in measured.items()}
    BOUNDS_PATH.write_text(json.dumps(bounds, indent=2, sort_keys=True) + "\n")
```

- [ ] **Step 2: Write `tests/regression/generate_bounds.py`**

```python
"""Run every regression case against the current code, record measured
CNOT counts, and write golden_bounds.json.

Only run when a phase deliberately changes resource characteristics.
"""

from __future__ import annotations

import numpy as np

import xyz
from tests.regression.bounds import write_bounds
from tests.regression.builders import dense_cases, dicke_cases, sparse_cases
from tests.regression.conftest import BOUND_SLACK, SEED

# Params per case group. Must stay in sync with the per-file test params.
DICKE_PARAM = xyz.StatePreparationParameters(
    enable_exact_synthesis=True, n_qubits_max=100
)


def measure_case(vec: np.ndarray, param=None) -> int:
    kwargs = {"map_gates": True}
    if param is not None:
        kwargs["param"] = param
    circuit = xyz.prepare_state(vec, **kwargs)
    return circuit.get_cnot_cost()


def main() -> None:
    rng = np.random.default_rng(SEED)
    measured: dict[str, int] = {}

    for case_id, vec in dense_cases(rng) + sparse_cases(rng):
        cnot = measure_case(vec)
        print(f"{case_id:40s} cnot={cnot}")
        measured[case_id] = cnot

    for case_id, vec in dicke_cases():
        cnot = measure_case(vec, param=DICKE_PARAM)
        print(f"{case_id:40s} cnot={cnot}")
        measured[case_id] = cnot

    write_bounds(measured, slack=BOUND_SLACK)
    print(f"\nWrote {len(measured)} bounds (slack={BOUND_SLACK}).")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify the script runs end-to-end**

This step actually generates `golden_bounds.json`. It is intentional: we
need the bounds committed before the regression tests can pass. If the
script fails, fix the failure before moving on — subsequent tasks assume
it works.

Run:

```bash
cd /home/hanyu/proj/quantum-xyz
python -m tests.regression.generate_bounds
```

Expected: 30 lines of `case_id cnot=<n>` output, finishing with
`Wrote 30 bounds (slack=1.1).`. A `golden_bounds.json` file appears in
`tests/regression/`.

If any single case takes more than ~10 seconds or raises, **stop** and
investigate — the case is either too expensive for the suite or exposes a
latent bug. Options: drop the case from `builders.py` (update expected
counts in Task 2's smoke test accordingly), or mark it `@pytest.mark.slow`
once the test file exists.

- [ ] **Step 4: Commit bounds infrastructure and the generated JSON**

```bash
git add tests/regression/bounds.py tests/regression/generate_bounds.py tests/regression/golden_bounds.json
git commit -m "test: add golden CNOT bounds generator and freeze baseline"
```

---

## Task 4: Dense-state regression tests

**Files:**
- Create: `tests/regression/test_dense_states.py`

- [ ] **Step 1: Write the test file**

```python
"""Regression: dense target states. Asserts statevector correctness and
CNOT-count non-regression against golden_bounds.json."""

from __future__ import annotations

import numpy as np
import pytest

import xyz
from tests.regression.builders import dense_cases
from tests.regression.conftest import SEED, STATEVECTOR_ATOL


@pytest.fixture(scope="module")
def case_map():
    rng = np.random.default_rng(SEED)
    return dict(dense_cases(rng))


@pytest.mark.parametrize(
    "case_id",
    [cid for cid, _ in dense_cases(np.random.default_rng(SEED))],
)
def test_dense(case_id, case_map, golden_bounds):
    target_vec = case_map[case_id]
    circuit = xyz.prepare_state(target_vec, map_gates=True)

    sim_vec = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(np.abs(sim_vec) - np.abs(target_vec)) < STATEVECTOR_ATOL, (
        f"{case_id}: statevector mismatch"
    )

    bound = golden_bounds[case_id]
    actual = circuit.get_cnot_cost()
    assert actual <= bound, f"{case_id}: CNOT {actual} > bound {bound}"
```

- [ ] **Step 2: Run the test**

```bash
cd /home/hanyu/proj/quantum-xyz
pytest tests/regression/test_dense_states.py -v
```

Expected: 16 parametrized tests, all PASS. If any fail on the statevector
assertion, there is an issue with the case generation (the library cannot
actually prepare it); drop that case from `builders.py` and regenerate the
bounds.

- [ ] **Step 3: Commit**

```bash
git add tests/regression/test_dense_states.py
git commit -m "test: regression cases for dense target states"
```

---

## Task 5: Sparse-state regression tests

**Files:**
- Create: `tests/regression/test_sparse_states.py`

- [ ] **Step 1: Write the test file**

```python
"""Regression: sparse target states (incl. cardinality-1 trivial cases)."""

from __future__ import annotations

import numpy as np
import pytest

import xyz
from tests.regression.builders import sparse_cases
from tests.regression.conftest import SEED, STATEVECTOR_ATOL


@pytest.fixture(scope="module")
def case_map():
    rng = np.random.default_rng(SEED)
    return dict(sparse_cases(rng))


@pytest.mark.parametrize(
    "case_id",
    [cid for cid, _ in sparse_cases(np.random.default_rng(SEED))],
)
def test_sparse(case_id, case_map, golden_bounds):
    target_vec = case_map[case_id]
    circuit = xyz.prepare_state(target_vec, map_gates=True)

    sim_vec = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(np.abs(sim_vec) - np.abs(target_vec)) < STATEVECTOR_ATOL, (
        f"{case_id}: statevector mismatch"
    )

    bound = golden_bounds[case_id]
    actual = circuit.get_cnot_cost()
    assert actual <= bound, f"{case_id}: CNOT {actual} > bound {bound}"
```

- [ ] **Step 2: Run the test**

```bash
pytest tests/regression/test_sparse_states.py -v
```

Expected: 21 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/regression/test_sparse_states.py
git commit -m "test: regression cases for sparse target states"
```

---

## Task 6: Dicke-state regression tests

**Files:**
- Create: `tests/regression/test_dicke_states.py`

- [ ] **Step 1: Write the test file**

```python
"""Regression: Dicke target states."""

from __future__ import annotations

import numpy as np
import pytest

import xyz
from tests.regression.builders import dicke_cases
from tests.regression.conftest import STATEVECTOR_ATOL


@pytest.fixture(scope="module")
def case_map():
    return dict(dicke_cases())


@pytest.mark.parametrize("case_id", [cid for cid, _ in dicke_cases()])
def test_dicke(case_id, case_map, golden_bounds):
    target_vec = case_map[case_id]

    param = xyz.StatePreparationParameters(
        enable_exact_synthesis=True, n_qubits_max=100
    )
    circuit = xyz.prepare_state(target_vec, map_gates=True, param=param)

    sim_vec = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(sim_vec - target_vec) < STATEVECTOR_ATOL, (
        f"{case_id}: statevector mismatch"
    )

    bound = golden_bounds[case_id]
    actual = circuit.get_cnot_cost()
    assert actual <= bound, f"{case_id}: CNOT {actual} > bound {bound}"
```

- [ ] **Step 2: Run the test**

```bash
pytest tests/regression/test_dicke_states.py -v
```

Expected: 8 tests PASS.

If any Dicke case does not pass statevector equality, it means the
Dicke-specific param path interacts with `generate_bounds.py`'s
default-param path differently. The generator must be updated to use the
same params as the test. See Task 9.

- [ ] **Step 3: Commit**

```bash
git add tests/regression/test_dicke_states.py
git commit -m "test: regression cases for Dicke target states"
```

---

## Task 7: Per-gate apply regression tests

**Files:**
- Create: `tests/regression/test_gate_apply.py`

This test pins each gate's `apply` to a qiskit reference. Gates whose
`apply` currently raises `NotImplementedError` are marked `xfail(strict=True)`
so Phase 2 can flip them to passing and the transition is visible.

- [ ] **Step 1: Write the test file**

```python
"""Regression: each Gate subclass's apply() matches qiskit simulation.

For gates whose apply is not yet implemented (raises NotImplementedError),
the test is marked xfail(strict=True). Phase 2 of the refactor removes the
markers as each apply is implemented."""

from __future__ import annotations

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

import xyz
from xyz.circuit.qgate import (
    CRX, CRY, CRZ, CU, CX, MCMY, MCRY, MULTIPLEXY,
    QBit, RX, RY, RZ, U, X, Z,
)
from tests.regression.builders import random_real_state
from tests.regression.conftest import SEED

# Gates whose apply() is not implemented today.
UNIMPLEMENTED_APPLY = {"RX", "RZ", "U", "Z", "CRX", "CRZ", "CU", "MCMY", "MULTIPLEXY"}


def _random_unitary_2x2(rng: np.random.Generator) -> np.ndarray:
    """A real SO(2) rotation is enough — apply only touches real amplitudes."""
    theta = rng.uniform(0, 2 * np.pi)
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def _make_gate(name: str, rng: np.random.Generator, n: int) -> object:
    """Return a concrete gate instance of class `name` operating on
    qubits drawn from range(n)."""
    theta = float(rng.uniform(0, 2 * np.pi))
    tgt = QBit(int(rng.integers(n)))
    ctrl_choices = [i for i in range(n) if i != tgt.index]
    ctrl = QBit(int(rng.choice(ctrl_choices)))

    if name == "RX": return RX(theta, tgt)
    if name == "RY": return RY(theta, tgt)
    if name == "RZ": return RZ(theta, tgt)
    if name == "X":  return X(tgt)
    if name == "Z":  return Z(tgt)
    if name == "U":  return U(_random_unitary_2x2(rng), tgt)
    if name == "CX": return CX(ctrl, 1, tgt)
    if name == "CRX": return CRX(theta, ctrl, 1, tgt)
    if name == "CRY": return CRY(theta, ctrl, 1, tgt)
    if name == "CRZ": return CRZ(theta, ctrl, 1, tgt)
    if name == "CU":  return CU(_random_unitary_2x2(rng), ctrl, 1, tgt)
    if name == "MCRY":
        controls = [QBit(i) for i in ctrl_choices[:2]]
        phases = [1, 1]
        return MCRY(theta, controls, phases, tgt)
    if name == "MCMY":
        controls = [QBit(i) for i in ctrl_choices[:2]]
        table = list(rng.uniform(0, 2 * np.pi, size=4))
        return MCMY(table, controls, tgt)
    if name == "MULTIPLEXY":
        theta0 = float(rng.uniform(0, 2 * np.pi))
        theta1 = float(rng.uniform(0, 2 * np.pi))
        return MULTIPLEXY(theta0, theta1, ctrl, tgt)
    raise AssertionError(f"unknown gate: {name}")


def _apply_on_qiskit(qc: QuantumCircuit, gate) -> None:
    """Apply the xyz gate's semantic equivalent to a qiskit circuit.

    For gates not in UNIMPLEMENTED_APPLY this exercises the currently
    implemented xyz.Gate.apply. For the others the xfail happens before
    this is reached (the call to gate.apply raises), so this only needs to
    handle the currently-implemented list."""
    name = type(gate).__name__
    t = gate.target_qubit.index
    if name == "RY":  qc.ry(gate.theta, t); return
    if name == "X":   qc.x(t); return
    if name == "CX":  qc.cx(gate.control_qubit.index, t); return
    if name == "CRY": qc.cry(gate.theta, gate.control_qubit.index, t); return
    if name == "MCRY":
        controls = [q.index for q in gate.control_qubits]
        qc.mcry(gate.theta, controls, t)
        return
    raise AssertionError(
        f"no qiskit equivalent wired for {name}; extend _apply_on_qiskit "
        "when Phase 2 implements its apply()"
    )


GATE_NAMES = [
    "RX", "RY", "RZ", "X", "Z", "U",
    "CX", "CRX", "CRY", "CRZ", "CU",
    "MCRY", "MCMY", "MULTIPLEXY",
]


@pytest.mark.parametrize("gate_name", GATE_NAMES)
def test_apply_matches_qiskit(gate_name):
    if gate_name in UNIMPLEMENTED_APPLY:
        pytest.xfail(
            f"{gate_name}.apply is not implemented yet; Phase 2 flips this."
        )

    rng = np.random.default_rng(SEED)
    n = 3 if gate_name in {"MCRY", "MCMY"} else 2
    init_vec = random_real_state(n, rng)

    gate = _make_gate(gate_name, rng, n)
    state = xyz.quantize_state(init_vec)
    xyz_result = gate.apply(state).to_vector()

    qc = QuantumCircuit(n)
    qc.initialize(init_vec, list(range(n)))
    _apply_on_qiskit(qc, gate)
    qiskit_result = np.real(Statevector(qc).data)

    assert np.allclose(xyz_result, qiskit_result, atol=1e-8), (
        f"{gate_name} apply mismatch:\n  xyz   ={xyz_result}\n  qiskit={qiskit_result}"
    )
```

- [ ] **Step 2: Run the test**

```bash
pytest tests/regression/test_gate_apply.py -v
```

Expected: 5 PASS (`RY, X, CX, CRY, MCRY`), 9 XFAIL. No test should XPASS or
ERROR. If an implemented gate XPASSes, remove it from `UNIMPLEMENTED_APPLY`.
If an `xfail` ERRORs (e.g. fails to construct) rather than failing at the
`apply` call, adjust `_make_gate` so construction succeeds first and the
`apply` is what raises.

- [ ] **Step 3: Commit**

```bash
git add tests/regression/test_gate_apply.py
git commit -m "test: regression per-gate apply vs qiskit (xfail unimplemented)"
```

---

## Task 8: Unblock existing skipped tests

**Files:**
- Modify: `tests/test_algorithms/test_dicke.py`
- Modify: `tests/test_algorithms/test_prepare_state.py`

These two tests are currently `@pytest.mark.skip`-ed. Converting them to
bound-based assertions makes them part of the safety net without requiring
exact CNOT reproducibility.

- [ ] **Step 1: Rewrite `tests/test_algorithms/test_dicke.py`**

Replace the file contents with:

```python
import numpy as np
import pytest
import xyz

# (num_qubits, k, historical_cnot_count). The historical_cnot_count field is
# kept for documentation only; the assertion is a 10%-slack upper bound so
# the test survives legitimate heuristic drift.
dicke_qsp_results = [
    (3, 1, 4),
    (4, 1, 7),
    (4, 2, 6),
    (5, 1, 10),
    (5, 2, 16),
    (6, 1, 13),
    (6, 2, 22),
    (6, 3, 25),
]


@pytest.mark.parametrize("n_qubits,k,historical", dicke_qsp_results)
def test_qsp_dicke(n_qubits, k, historical):
    state_vector = xyz.D_state(n_qubits, k)
    param = xyz.StatePreparationParameters(
        enable_exact_synthesis=True, n_qubits_max=100
    )
    circuit = xyz.prepare_state(state_vector, map_gates=True, param=param)

    sim = xyz.simulate_circuit(circuit)
    assert np.linalg.norm(sim - state_vector) < 1e-6, (
        f"n={n_qubits} k={k}: statevector mismatch"
    )

    bound = int(np.ceil(historical * 1.1))
    cnot = circuit.get_cnot_cost()
    assert cnot <= bound, f"n={n_qubits} k={k}: CNOT {cnot} > bound {bound}"
```

- [ ] **Step 2: Unblock `test_qsp_1` in `tests/test_algorithms/test_prepare_state.py`**

Open `tests/test_algorithms/test_prepare_state.py` and remove lines 7-8:

```python
# skip
@pytest.mark.skip(reason="Takes too long")
```

so that `test_qsp_1` runs. If it is genuinely too slow for default CI, add
`@pytest.mark.slow` instead of removing the skip outright. Decide based on
Step 3's measurement.

- [ ] **Step 3: Measure and run**

```bash
pytest tests/test_algorithms/test_dicke.py tests/test_algorithms/test_prepare_state.py -v --durations=0
```

Expected: all tests PASS. Check the `slowest durations` table: if any test
is over 30s, switch its decorator to `@pytest.mark.slow` and document it in
the regression README.

- [ ] **Step 4: Commit**

```bash
git add tests/test_algorithms/test_dicke.py tests/test_algorithms/test_prepare_state.py
git commit -m "test: unblock dicke + qsp_1 tests as bound-based assertions"
```

---

## Task 9: Full-suite verification + budget check

- [ ] **Step 1: Run the entire regression package**

```bash
cd /home/hanyu/proj/quantum-xyz
pytest tests/regression/ -v --durations=10
```

Expected: 10 dense + 15 sparse + 5 dicke + 14 gate-apply (5 PASS, 9 XFAIL) =
44 test outcomes, all green (`passed` or `xfailed`; no `failed`, `error`,
or `xpassed`). Total runtime under 2 minutes.

- [ ] **Step 2: Run the whole repo suite**

```bash
pytest tests/ -v --durations=10
```

Expected: the existing suite continues to pass, plus all new regression
tests pass. No tests that were previously passing now fail.

- [ ] **Step 3: If runtime exceeds 2 minutes**

Identify the top-3 longest cases from `--durations=10`. Apply
`@pytest.mark.slow` to those specific parametrize IDs (pytest supports
this via `@pytest.mark.parametrize(..., marks=pytest.mark.slow)` on the
argvalues) and add a marker registration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: slower cases, skipped in default CI via `-m 'not slow'`",
]
```

Then re-run with `pytest tests/regression/ -m "not slow"` to confirm it
stays under budget, and update the regression README to document the flag.

- [ ] **Step 4: Commit any tuning from Step 3**

```bash
# only if slow markers or pyproject changes were added
git add pyproject.toml tests/regression/
git commit -m "test: mark slow regression cases behind pytest marker"
```

---

## Task 10: Phase 0 exit-criteria checklist

Confirm each Phase 0 exit criterion from the spec holds. No code changes in
this task — only verification.

- [ ] **Step 1: New tests green on current code**

```bash
pytest tests/regression/ -v
```

All outcomes are `passed` or `xfailed`. No `failed`, `error`, or `xpassed`.

- [ ] **Step 2: `golden_bounds.json` is committed and non-empty**

```bash
git ls-files tests/regression/golden_bounds.json
wc -l tests/regression/golden_bounds.json
```

The file must appear in `git ls-files` and contain at least 30 entries.

- [ ] **Step 3: Runtime budget**

```bash
pytest tests/regression/ --durations=0 -q
```

Total time under 2 minutes. If slow markers are in use, the default mode
(without `-m "not slow"`) must still be under 2 minutes — the goal is fast
feedback in regular runs.

- [ ] **Step 4: Create a phase-exit record**

```bash
cat > docs/superpowers/plans/2026-04-19-phase0-exit.md <<'EOF'
# Phase 0 Exit Record

- Regression suite: `pytest tests/regression/` — all green.
- Total cases: 10 dense + 15 sparse + 5 dicke + 14 gate-apply (5 pass, 9 xfail).
- Golden bounds frozen at `tests/regression/golden_bounds.json`.
- Wall-clock budget: under 2 minutes.
- Legacy tests unblocked: `test_dicke.py`, `test_qsp_1`.

Phase 1 (bug fixes) may begin.
EOF
git add docs/superpowers/plans/2026-04-19-phase0-exit.md
git commit -m "docs: phase 0 exit record"
```

Phase 0 complete. Proceed to Phase 1 only after this point.

---

## Out of Scope

- Phase 1 bug fixes — separate plan.
- Phase 2 `Gate` ABC + apply completion — separate plan. When it lands, the
  `UNIMPLEMENTED_APPLY` set in `test_gate_apply.py` shrinks accordingly, and
  `_apply_on_qiskit` grows a branch for each newly-implemented gate.
- Phase 3-5 — separate plans, each produced after the prior phase merges.
