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
