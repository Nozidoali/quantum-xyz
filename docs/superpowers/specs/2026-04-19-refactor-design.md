# quantum-xyz Refactor Design

**Date:** 2026-04-19
**Scope:** All 5 refactor items — bug fixes, `Gate` ABC, `qgate.py` split, strategy pattern for state preparation, `import *` cleanup.
**API compatibility:** Research-code mode. Top-level symbols (`xyz.prepare_state`, `xyz.QState`, etc.) remain importable. Internal paths and sub-package layout can change freely. `example/` and `tests/` imports are updated as part of the refactor.
**Delivery:** 6 phases, each independently committable and CI-green.

---

## Goals

1. Break the 858-line `xyz/circuit/qgate.py` into focused modules.
2. Introduce a real `Gate` ABC so every gate honors a uniform contract.
3. Replace the monolithic `_prepare_state_rec` with a strategy pattern.
4. Fix known bugs in `prepare_state.py` and `qgate.py` that today's tests miss.
5. Make the package layout reflect concerns (gates / decomposition / synthesis / passes / io) instead of the current `circuit` vs `algorithms` split.
6. Replace every `from x import *` with explicit `__all__`.

## Non-Goals

- No new synthesis algorithms. No new gate types.
- No property-based tests, no coverage-number targets.
- No backwards-compat shims. Imports under the old paths stop working (except the top-level `xyz.*` symbols listed in Phase 5).

---

## Target Package Structure

```
xyz/
  gates/
    __init__.py                # explicit __all__
    types.py                   # QGateType enum, QBit, RotationTrait,
                               # UnitaryTrait, ControlledTrait,
                               # MultiControlledTrait
    base.py                    # Gate ABC
    single.py                  # X, Z, RX, RY, RZ, U
    controlled.py              # CX, CRX, CRY, CRZ, CU
    multi_controlled.py        # MCRY, MCMY, MULTIPLEXY
    cost_tables.py             # MCRY_CNOT_COST (int keys)
  decomposition/
    zyz.py                     # unitary_zyz_decomposition, to_special_unitary
    gray_code.py               # find_thetas, decompose_mcry,
                               # control_sequence_to_gates
    mcry.py                    # map_mcry, map_mcmy, map_muxy,
                               # map_mcry_linear, theta_to_unitary,
                               # unitary_convert
  state/
    qstate.py                  # moved from xyz/circuit/qstate.py
    ops.py                     # quantize_state and state helpers
  circuit/
    qcircuit.py                # QCircuit container (unchanged logic)
  synthesis/                   # was algorithms/initialization/
    prepare_state.py           # thin facade
    params.py                  # StatePreparationParameters, Stats
    dicke.py                   # was deterministic_dicke_state.py
    support_reduction/         # preserved sub-package
    strategies/
      base.py                  # SynthesisStrategy ABC
      trivial.py               # cardinality==1 short circuit
      exact_cnot.py            # was exact_cnot_synthesis.py
      m_flow.py                # was sparse_state_synthesis.py
      n_flow.py                # was n_flow.py
  passes/                      # was algorithms/optimization/
    resynthesis.py
    mapping.py
  io/                          # was external/
    qasm.py                    # merged read_qasm + write_qasm
    qiskit_bridge.py           # merged to_qiskit + qiskit_opt + special_gates
    simulate.py
  utils/
    timer.py
    colors.py
  __init__.py                  # only re-exports the public API (Phase 5)
```

Top-level symbols that stay importable from `xyz`:
`prepare_state`, `QState`, `QCircuit`, `quantize_state`, `simulate_circuit`,
`to_qiskit`, `StatePreparationParameters`, `stopwatch`, `D_state`.

---

## Gate ABC Contract

```python
# xyz/gates/base.py
class Gate(ABC):
    qgate_type: QGateType

    @abstractmethod
    def qubits(self) -> list[QBit]: ...
    @abstractmethod
    def apply(self, state: QState) -> QState: ...
    @abstractmethod
    def cnot_cost(self) -> int: ...

    def conjugate(self) -> "Gate":
        raise NotImplementedError(f"{type(self).__name__} has no conjugate")

    def __str__(self) -> str: ...
```

**Traits (data-only mixins) live in `types.py`:**
`RotationTrait`, `UnitaryTrait`, `ControlledTrait`, `MultiControlledTrait`.
Concrete gates use MRO: `class CRY(Gate, RotationTrait, ControlledTrait): ...`.

**Invariants:**
1. `apply` is pure — does not mutate its `state` argument, returns a new `QState`.
2. `cnot_cost` returns the CNOT upper bound after mapping to `{U2, CX}`; gates
   that contribute no CNOTs return 0.
3. `qubits()` returns controls first, then targets, with stable order by index.
4. Every concrete gate implements `apply`; there is no `NotImplementedError`
   fallback for `apply` on any subclass after Phase 2.

**Naming: getters are dropped.**

| Old                            | New               |
|--------------------------------|-------------------|
| `get_cnot_cost()`              | `cnot_cost()`     |
| `get_qgate_type()`             | `qgate_type` (attribute) |
| `get_control_qubit()`          | `control_qubits` (attribute, always a list) |
| `get_control_qubits()`         | `control_qubits` (attribute) |
| `get_target_qubit()`           | `target_qubit` (attribute) |
| `get_phase()` / `get_phases()` | `phase` / `phases` (attribute) |
| `get_theta()`                  | `theta` (attribute) |
| `get_unitary()`                | `unitary` (attribute) |
| `get_alpha/beta/gamma()`       | `alpha/beta/gamma` (attribute) |

---

## `qgate.py` Decomposition

858-line source → six files under `xyz/gates/` plus three under `xyz/decomposition/`.
Target: no file in `gates/` exceeds 200 lines; `xyz/circuit/qgate.py` is deleted.

**`gates/types.py`** (~60 lines)
- `QGateType` enum (unchanged)
- `QBit` (unchanged)
- `RotationTrait`, `UnitaryTrait`, `ControlledTrait`, `MultiControlledTrait`

**`gates/base.py`** (~40 lines)
- `Gate` ABC only

**`gates/single.py`** (~120 lines)
- `X, Z, RX, RY, RZ, U`
- New `apply` implementations: `RX`, `RZ`, `U`, `Z`

**`gates/controlled.py`** (~150 lines)
- `CX, CRX, CRY, CRZ, CU`
- New `apply` implementations: `CRX`, `CRZ`, `CU`

**`gates/multi_controlled.py`** (~100 lines)
- `MCRY, MCMY, MULTIPLEXY`
- New `apply` implementations: `MCMY`, `MULTIPLEXY`

**`gates/cost_tables.py`** (~30 lines)
- `MCRY_CNOT_COST` with **int keys** (was string-keyed)
- `MCRY.cnot_cost()` looks up the table; an unsupported control count raises
  with a clear message

**`decomposition/` — pure functions, no `Gate` instances on input:**
- `zyz.py`: `unitary_zyz_decomposition`, `to_special_unitary`
- `gray_code.py`: `find_thetas`, `decompose_mcry`, `control_sequence_to_gates`
- `mcry.py`: `map_mcry`, `map_mcmy`, `map_muxy`, `map_mcry_linear`,
  `theta_to_unitary`, `unitary_convert`
  - **Bug fix:** `map_muxy` currently uses `gate.type` (attribute does not
    exist), so the function is unreachable. Corrected to `gate.qgate_type`.

---

## Strategy Pattern for `prepare_state`

```python
# xyz/synthesis/strategies/base.py
class SynthesisStrategy(ABC):
    def __init__(self, engine: "SynthesisEngine"):
        self.engine = engine

    @abstractmethod
    def applicable(
        self, state: QState, param: StatePreparationParameters
    ) -> bool: ...

    @abstractmethod
    def synthesize(
        self, circuit: QCircuit, state: QState
    ) -> tuple[list[Gate], int]: ...
```

```python
# xyz/synthesis/prepare_state.py
class SynthesisEngine:
    def __init__(self, param, stats, verbose_level):
        self.param = param
        self.stats = stats or Stats()
        self.verbose_level = verbose_level
        self.strategies = [
            TrivialStrategy(self),
            ExactCNOTStrategy(self),
            MFlowStrategy(self),
            NFlowStrategy(self),
        ]

    def run(self, circuit, state):
        # 1. Support reduction (if param.enable_compression).
        # 2. Short-circuit strategies (Trivial, ExactCNOT): if applicable,
        #    use their result exclusively.
        # 3. Competing strategies (MFlow, NFlow): run each, pick minimum
        #    cnot_count.
```

Short-circuit vs competing semantics lives in the engine, not in the
strategies themselves.

`prepare_state` is a thin facade that normalizes inputs (np.ndarray → QState),
picks a default `StatePreparationParameters` via the existing CNOT-estimation
heuristic, creates the engine, and runs it.

---

## Bug Fixes (Phase 1, pre-refactor)

1. **Mutable default argument** — `stats: Stats = Stats()` in `prepare_state`
   and `_prepare_state_rec`. Changed to `stats=None`, initialized inside.
2. **`param` dropped** — `_prepare_state_rec` takes `param=param` through
   `**kwargs`, then overwrites it with a fresh `StatePreparationParameters()`
   and re-applies `kwargs`. External `param` is silently discarded.
3. **`Z.apply` dead code + bug** — writes to an `index_to_weight` dict, then
   raises `NotImplementedError` unconditionally. Replaced with a real phase-flip
   implementation.
4. **`map_muxy` unreachable** — uses `gate.type` which does not exist on
   `MULTIPLEXY`. Corrected to `gate.qgate_type`.
5. **`stats is not None` dead check** — the default is a `Stats()` instance,
   never `None`. Removed.
6. **`enable_reindex=True` raises inside `_prepare_state_rec`** — the branch
   calls `reindex_circuit(circuit, state)` then unconditionally raises
   `NotImplementedError`. The flag stays on `StatePreparationParameters` (default
   `False`) but Phase 1 moves the raise to the top of the branch before any
   side-effect call, with a message pointing at the unimplemented status.

Each fix gets a dedicated unit test.

---

## Phase Plan

Strict sequential order: 0 → 1 → 2 → 3 → 4 → 5. Phase 0 tests must remain
green through every subsequent phase; a red run is a rollback.

### Phase 0 — Test Safety Net

**Additions under `tests/regression/`:**
- `conftest.py` — shared fixtures (fixed RNG seeds, target-state builders)
- `golden_bounds.json` — `{case_id: cnot_bound}`, generated once and frozen
- `test_dense_states.py`, `test_sparse_states.py`, `test_dicke_states.py`
- `test_gate_apply.py` — every concrete gate's `apply` vs a qiskit reference

**Actions:**
- Remove `@pytest.mark.skip` from `test_dicke.py` and `test_qsp_1`, convert
  their exact-CNOT assertions to `<= bound` assertions.
- Add `xfail` placeholders for the `apply` methods that currently raise
  `NotImplementedError` (lifted to passing in Phase 2).

**Exit criteria:**
- All regression tests green on the **current** (un-refactored) codebase.
- `golden_bounds.json` committed.
- `pytest tests/regression/` runs in under 2 minutes locally and in CI.

### Phase 1 — Bug Fixes Only

In the existing file tree, apply the 6 bug fixes above. Add a unit test per
fix. No reorganization.

**Exit criteria:** Phase 0 suite green; new bug-fix tests green.

### Phase 2 — Gate ABC and `apply` Completion

- Create `xyz/gates/types.py` and `xyz/gates/base.py` alongside the existing
  `qgate.py` (still only one file with gate classes at this point).
- Make every gate inherit from the new `Gate` ABC.
- Rename getters (`get_cnot_cost` → `cnot_cost`, etc.) across the whole
  repository in one sweep.
- Implement `apply` for `RX, RZ, U, Z, CRX, CRZ, CU, MCMY, MULTIPLEXY`.

**Exit criteria:**
- Phase 0 suite green.
- `test_gate_apply.py` covers every concrete gate and passes.
- `grep -r "get_cnot_cost\|get_qgate_type\|get_control_qubit\|get_target_qubit\|get_phase\|get_theta\|get_unitary" xyz/` returns nothing.

### Phase 3 — Split `qgate.py`

Move gate classes and helper functions into the structure defined above
(`gates/*.py` and `decomposition/*.py`). Delete `xyz/circuit/qgate.py`.

**Exit criteria:**
- Phase 0 suite green.
- No file in `xyz/gates/` exceeds 200 lines.
- `find xyz -name qgate.py` returns nothing.

### Phase 4 — Strategy Pattern and Package Reorganization

- `xyz/algorithms/initialization/` → `xyz/synthesis/`
- `xyz/algorithms/optimization/` → `xyz/passes/`
- `xyz/external/` → `xyz/io/`
- `xyz/circuit/qstate.py` → `xyz/state/qstate.py`
- `_prepare_state_rec` split into `SynthesisEngine` plus four strategy
  classes.
- Update every import in `example/` and `tests/`.

**Exit criteria:**
- Phase 0 suite green.
- `example/synthesize_dicke.py`, `example/resynthesize_circuit.py`, and
  `example/run_simulation.py` all run.
- `xyz/algorithms/` does not exist.

### Phase 5 — Explicit Exports

- Every `__init__.py` declares `__all__`.
- `xyz/__init__.py` re-exports only: `prepare_state`, `QState`, `QCircuit`,
  `quantize_state`, `simulate_circuit`, `to_qiskit`,
  `StatePreparationParameters`, `stopwatch`, `D_state`.
- Remove every `from .x import *`.

**Exit criteria:**
- `grep -rn "from .* import \*" xyz/` returns nothing.
- `python -c "import xyz; xyz.prepare_state"` works.
- A representative consumer script (`example/synthesize_dicke.py`) runs.

---

## Testing Strategy

Correctness is verified by comparing statevectors against qiskit simulation.
Resource regression is guarded by per-case CNOT-count bounds.

### Test matrix (~45 cases)

**Dense (`test_dense_states.py`, 16 cases)**
- 3/4/5/6 qubits, three random Haar-sampled targets each (seeded) → 12
- 3/4/5/6 qubits, one uniform superposition each → 4

**Sparse (`test_sparse_states.py`, 21 cases)**
- 4/5/6 qubits × cardinality ∈ {2, 4, 8}, two random support sets each → 18
- 3/4/5 qubits with cardinality 1 (trivial short-circuit) → 3

**Dicke (`test_dicke_states.py`, 8 cases)**
- `(n, k)` pairs from the existing `dicke_qsp_results` table

### Per-case assertions

```python
def test_case(case):
    target = build_target(case)
    target_vec = target.to_vector() if isinstance(target, QState) else target

    circuit = xyz.prepare_state(target, map_gates=True)
    sim_vec = xyz.simulate_circuit(circuit)

    # Functional correctness
    assert np.linalg.norm(np.abs(sim_vec) - np.abs(target_vec)) < 1e-6

    # Resource non-regression
    assert circuit.get_cnot_cost() <= golden_bounds[case.id]
```

`golden_bounds.json` is generated once on the un-refactored code: record
measured CNOT counts × 1.1 (ceiling). After that the file is read-only — it
is updated only when a phase deliberately changes resource characteristics,
and such a change is called out explicitly in its commit message.

### Gate apply unit tests (`test_gate_apply.py`)

```python
@pytest.mark.parametrize("gate_cls",
    [RX, RY, RZ, X, Z, U, CX, CRX, CRY, CRZ, CU, MCRY, MCMY, MULTIPLEXY])
def test_apply_matches_qiskit(gate_cls):
    state = random_qstate(seed=...)
    gate = random_instance(gate_cls)
    xyz_result = gate.apply(state).to_vector()

    qc = QuantumCircuit(state.num_qubits)
    qc.initialize(state.to_vector())
    apply_to_qiskit(qc, gate)
    qiskit_result = Statevector(qc).data

    assert np.allclose(xyz_result, qiskit_result, atol=1e-8)
```

Phase 2 promotes the currently-`xfail`-ed cases (RX, RZ, U, Z, CRX, CRZ, CU,
MCMY, MULTIPLEXY) to required-pass.

### Budgets

- `pytest tests/regression/` < 2 min on developer machines and CI.
- Larger cases (>6 qubits, or sparse with large cardinality) are marked
  `@pytest.mark.slow`; CI does not run them by default but each merge runs
  them manually at least once.
- Every random draw uses a fixed seed declared in `conftest.py`.

### Out of scope

- Property-based testing (hypothesis) — disproportionate for research code.
- Coverage-percentage targets — easy to game, not a correctness signal.
- Exhaustive per-internal-function unit tests — regression tests cover
  end-to-end behavior; Phase 2 gate-apply tests cover the gate layer.

---

## Risks

- **Gate `apply` completion scope.** If the math for `CU.apply` or
  `MULTIPLEXY.apply` proves harder than the other fills, Phase 2 may slip.
  Mitigation: the scope is bounded (11 missing `apply` methods, all
  single-gate-level), and `test_gate_apply.py` defines the success signal
  clearly.
- **Golden bound drift.** Phase 4's strategy-pattern reshuffle could change
  tie-breaking between `MFlow` and `NFlow` and push a case above its bound.
  Mitigation: the 10% slack absorbs routine variation; a breach means
  inspecting whether the change is an actual regression before bumping the
  bound.
- **Import-path churn.** Phase 4 moves many files. Mitigation: staged as its
  own phase with `example/` runs and the Phase 0 suite gating the merge.
