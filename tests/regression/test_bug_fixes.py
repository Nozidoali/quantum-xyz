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
