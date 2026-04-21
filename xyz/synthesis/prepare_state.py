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

__all__ = [
    "prepare_state",
]

from typing import Optional, Union

import numpy as np

from xyz.circuit import QCircuit, QState, quantize_state
from xyz.synthesis.engine import SynthesisEngine
from xyz.synthesis.params import (
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
