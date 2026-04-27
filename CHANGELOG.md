# Changelog

All notable changes to `quantum-xyz` are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased] — 0.2.0 candidate

This release is the result of a five-phase refactor (see
`docs/superpowers/specs/2026-04-19-refactor-design.md` and the matching
plan + exit records under `docs/superpowers/plans/`). It is breaking on
purpose: the public API is now a deliberately narrow surface, gates have
a uniform contract, and the package layout reflects responsibilities
instead of historical accident.

### Breaking changes

#### Public API narrowed

`from xyz import *` (and any `import xyz; xyz.<name>`) now resolves to
exactly nine symbols:

```
prepare_state           # the synthesis entry point
QState                  # the state data type
QCircuit                # the circuit container
quantize_state          # numpy/string → QState
simulate_circuit        # QCircuit → numpy statevector (via qiskit)
to_qiskit               # QCircuit → qiskit.QuantumCircuit
StatePreparationParameters
stopwatch
D_state                 # Dicke state factory
```

Everything else is at its sub-package: `from xyz.gates import X, CRY, ...`,
`from xyz.state import rand_state, get_ry_angles, ...`,
`from xyz.synthesis import QSPDatabase, exact_cnot_synthesis, ...`,
`from xyz.passes import resynthesis`, `from xyz.io import read_qasm, ...`.

#### Package layout

| Old | New |
|---|---|
| `xyz/circuit/qgate.py` (858 lines) | `xyz/gates/{base,types,single,controlled,multi_controlled,cost_tables}.py` + `xyz/decomposition/{zyz,gray_code,mcry}.py` |
| `xyz/algorithms/initialization/` | `xyz/synthesis/` |
| `xyz/algorithms/optimization/` | `xyz/passes/` |
| `xyz/external/` | `xyz/io/` |
| `xyz/circuit/qstate.py` | `xyz/state/qstate.py` |
| `tests/test_algorithms/` | `tests/test_synthesis/` |

#### Gate API: getters → attributes

Every getter on the gate hierarchy was dropped. Concrete data is now
plain attribute access; the only callable holdovers are `cnot_cost()`
and `qubits()`, which are abstract methods on the new `Gate` ABC.

| Old | New |
|---|---|
| `gate.get_cnot_cost()` | `gate.cnot_cost()` |
| `gate.get_qgate_type()` | `gate.qgate_type` |
| `gate.get_target_qubit()` | `gate.target_qubit` |
| `gate.get_control_qubit()` (singular) | `gate.control_qubits[0]` |
| `gate.get_control_qubits()` | `gate.control_qubits` |
| `gate.get_phase() / get_phases()` | `gate.phase` / `gate.phases` |
| `gate.get_theta()` | `gate.theta` |
| `gate.get_unitary()` | `gate.unitary` |
| `gate.get_alpha/beta/gamma()` | `gate.alpha / gate.beta / gate.gamma` |

`QCircuit.get_cnot_cost()` (the circuit-level method) keeps its name.

#### Legacy trait aliases removed

`UnitaryGate`, `RotationGate`, `ControlledGate`, `MultiControlledGate`,
`MultiRotationGate`, and the `QGate` alias are gone. Use the
`-Trait`-suffixed names from `xyz.gates.types` (`UnitaryTrait`,
`RotationTrait`, `ControlledTrait`, `MultiControlledTrait`) and
`Gate` from `xyz.gates.base`.

#### `_prepare_state_rec` no longer accepts `**kwargs`

It used to take `**kwargs` then silently rebuild `param` from defaults,
discarding the caller's parameters. The signature is now explicit
(`stats: Stats | None = None`, `param: StatePreparationParameters | None
= None`). Anything that called it positionally or with unknown keywords
will break.

#### `enable_reindex=True` raises immediately

The flag was unimplemented and used to call `reindex_circuit` (which
mutates state) before raising `NotImplementedError`. The raise now fires
at the top of the engine, before any side effect. The `reindex_circuit`
function and `xyz/synthesis/_reindex.py` have been deleted.

### Bug fixes

1. **Mutable-default `stats` argument.** `prepare_state` and the engine
   used `stats: Stats = Stats()` as defaults, sharing one instance across
   all default-call invocations. Defaults are `None` sentinels now, with
   in-function initialization.
2. **Caller-supplied `param` dropped.** `_prepare_state_rec` overwrote
   the incoming `param` with a default `StatePreparationParameters()`
   then merged unknown `**kwargs` (which included the original `param`,
   silently rejected by `param.update`). Fixed with an explicit
   parameter.
3. **`Z.apply`** populated a dict and then unconditionally raised
   `NotImplementedError`. Now actually flips the phase of amplitudes
   whose target-qubit bit is 1.
4. **`map_muxy` AttributeError.** Asserted on `gate.type`, which doesn't
   exist on `MULTIPLEXY` (the attribute is `qgate_type`). Anyone who
   triggered the `MULTIPLEX_Y` mapping path got an immediate crash.
5. **Dead `if stats is not None:` guards.** Three of them, all always
   true after fix #1. Removed.
6. **`stale gate.get_cnot_cost()` callers.** Two example scripts and a
   handful of internal modules still called the renamed getter; they
   would have crashed at runtime. Renamed.

### Added

- **`Gate` ABC** (`xyz.gates.base.Gate`). Abstract `apply`,
  `cnot_cost`, `qubits`. Optional `conjugate` (raises by default;
  subclasses override). Every concrete gate honors the contract.
- **8 missing `apply` implementations.** `RX`, `RZ`, `U`, `CRX`, `CRZ`,
  `CU`, `MCMY`, `MULTIPLEXY`. Under the library's real-amplitude
  `QState` convention, `RX`/`RZ` and their controlled cousins reduce to
  scalar `cos(θ/2)` multiplication on the enabled subspace.
- **Strategy pattern for state preparation.** `SynthesisEngine`
  orchestrates four `SynthesisStrategy` subclasses (`TrivialStrategy`,
  `ExactCNOTStrategy`, `MFlowStrategy`, `NFlowStrategy`). The first two
  short-circuit; the latter two compete and the engine picks the
  minimum CNOT count.
- **Regression test suite** (`tests/regression/`) with statevector
  correctness + frozen golden CNOT bounds across 10 dense, 15 sparse,
  and 5 Dicke target states. Plus per-gate `apply` tests against a
  qiskit reference.
- **Explicit `__all__`** on every leaf module and `__init__.py`. No
  `from x import *` remains anywhere in the package.

### Performance

- **150× speed-up for dense state preparation.** Bug #2's fix means
  dense targets now correctly take the n-flow (qubit-reduction) path
  instead of the m-flow (cardinality-reduction) path the bug was
  inadvertently routing them through. `dense_random_n4` cases dropped
  from ~135s each to ~0.07s each. The behavior was always available; the
  bug just hid it.

### Removed

- `xyz/circuit/qgate.py` (858-line monolith — split into `xyz/gates/*`
  and `xyz/decomposition/*`)
- `xyz/synthesis/_reindex.py` (`reindex_circuit` had no callers)
- `MultiRotationGate` (had no callers)
- Legacy trait class aliases (see Breaking Changes above)
- All `from x import *` in package code
- 6-line `Author / Created time / Last Modified time` metadata
  docstrings (29 files; git log/blame is the source of truth)
- Stale `# -*- encoding=utf8 -*-` magic comments (Python 3 default)

### Test suite

- `pytest tests/ -m "not slow"` is green: 77 passed, 1 skipped (qasm
  benchmark dir absent), 1 deselected (`test_qsp_1` slow-marked),
  ~10 seconds end-to-end on a slurm compute node.
- `tests/regression/` is the safety net for future refactors.
- `pyproject.toml` registers a `slow` pytest marker; the heavy
  `test_qsp_1` and any future slow cases are gated behind it.

## [0.1.0]

Initial release. See git history before this changelog landed.
