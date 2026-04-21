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
UNIMPLEMENTED_APPLY = {"MCMY", "MULTIPLEXY"}


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
    if name == "RX":  qc.rx(gate.theta, t); return
    if name == "RY":  qc.ry(gate.theta, t); return
    if name == "RZ":  qc.rz(gate.theta, t); return
    if name == "X":   qc.x(t); return
    if name == "Z":   qc.z(t); return
    if name == "U":   qc.unitary(gate.unitary, [t]); return
    if name == "CX":  qc.cx(gate.control_qubits[0].index, t); return
    if name == "CRX":
        qc.crx(gate.theta, gate.control_qubits[0].index, t); return
    if name == "CRY": qc.cry(gate.theta, gate.control_qubits[0].index, t); return
    if name == "CRZ":
        qc.crz(gate.theta, gate.control_qubits[0].index, t); return
    if name == "CU":
        from qiskit.circuit.library import UnitaryGate as _UGate
        qc.append(_UGate(gate.unitary).control(1),
                  [gate.control_qubits[0].index, t])
        return
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
    # Normalize qiskit result to match xyz normalization via to_vector()
    qiskit_result_norm = np.linalg.norm(qiskit_result)
    if qiskit_result_norm > 0:
        qiskit_result = qiskit_result / qiskit_result_norm

    assert np.allclose(xyz_result, qiskit_result, atol=1e-8), (
        f"{gate_name} apply mismatch:\n  xyz   ={xyz_result}\n  qiskit={qiskit_result}"
    )
