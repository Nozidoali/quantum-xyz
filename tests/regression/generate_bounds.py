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
