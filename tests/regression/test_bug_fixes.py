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

    Note: _prepare_state_rec was removed in Phase 4 Task 5 when the
    SynthesisEngine replaced it. Only the outer prepare_state facade
    signature is checked here.
    """
    import inspect

    sig_outer = inspect.signature(xyz.prepare_state)
    outer_default = sig_outer.parameters["stats"].default
    assert outer_default is None, (
        f"prepare_state stats default is {type(outer_default).__name__}; "
        "expected None to avoid mutable-default sharing across calls"
    )


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


def test_Z_apply_flips_target_phase():
    """Bug 3: Z.apply populates a dict then raises unconditionally.

    Expected behavior: flip the sign of every amplitude whose target-qubit
    bit is 1. A basis state |01> on (q0=low, q1=high), with target=q0, is
    unchanged in magnitude but flipped in sign if the q0 bit is 1.
    """
    from xyz.gates.types import QBit
    from xyz.gates.single import Z

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


def test_map_muxy_does_not_raise_attribute_error():
    """Bug 4: `map_muxy` references gate.type which does not exist on
    MULTIPLEXY (the attribute is `qgate_type`). Today the call raises
    AttributeError before producing any gates.
    """
    from xyz.gates.multi_controlled import MULTIPLEXY
    from xyz.gates.types import QBit
    from xyz.decomposition.mcry import map_muxy

    gate = MULTIPLEXY(
        theta0=0.3,
        theta1=0.5,
        control_qubit=QBit(0),
        target_qubit=QBit(1),
    )
    mapped = map_muxy(gate)  # must not raise
    assert len(mapped) > 0, "map_muxy produced an empty gate list"


def test_prepare_state_with_stats_none_still_works():
    """Bug 5 companion: `stats is not None` guards inside prepare_state and
    _prepare_state_rec were dead after Task 1's fix. Removing them is
    behavior-preserving only if the functions correctly initialize stats
    when the caller passes None. This test pins that behavior.
    """
    circuit = xyz.prepare_state(_trivial_state(), map_gates=True, stats=None)
    # A cardinality-1 trivial state produces a valid circuit with 0 CNOTs.
    assert circuit.get_cnot_cost() == 0


def test_enable_reindex_raises_before_side_effect():
    """Bug 6: enable_reindex=True must raise NotImplementedError and must
    never trigger support_reduction as a side-effect.

    In Phase 4 Task 5 the guard was moved to SynthesisEngine.run(), which
    fires before Phase 1 (support_reduction). We verify: (a) NotImplementedError
    is raised, and (b) the engine stats show zero support_reduction runs,
    confirming the guard fires before any work is done.
    """
    from xyz.algorithms.initialization.params import Stats

    param = StatePreparationParameters()
    param.enable_reindex = True
    stats = Stats()

    with pytest.raises(NotImplementedError):
        xyz.prepare_state(_trivial_state(), map_gates=True, param=param, stats=stats)

    assert stats.num_runs_support_reduction == 0, (
        f"support_reduction ran {stats.num_runs_support_reduction} time(s) "
        "before the NotImplementedError raise"
    )
