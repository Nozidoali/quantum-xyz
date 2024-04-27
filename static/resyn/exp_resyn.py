#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-11-16 17:06:22
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-17 00:55:53
"""

# pylint: disable=wrong-import-position
# pylint: skip-file

import numpy as np

from xyz import (
    quantize_state,
    stopwatch,
    W_state,
    D_state,
    rand_state,
    prepare_state,
    resynthesis,
    simulate_circuit,
    QState,
    QCircuit,
    to_qiskit,
    read_qasm,
    write_qasm,
    QBA_state
)
from xyz import StatePreparationParameters as Param

import pandas as pd

def generate_initial_circuit(state_vector: np.ndarray, data = {}) -> QCircuit:
    # synthesize the state using the best method
    state = quantize_state(state_vector)
    n = state.num_qubits
    m = len(state.index_set)
    enable_m_flow: bool = m*n < (1<<n)
    enable_n_flow: bool = ~enable_m_flow
    param = Param(
        enable_compression=False,
        enable_m_flow=enable_m_flow,
        enable_n_flow=enable_n_flow,
        enable_exact_synthesis=False,
    )
    with stopwatch("synthesis") as timer_old:
        circuit = prepare_state(
            state, map_gates=True, verbose_level=0, param=param
        )
    n_cnot = circuit.get_cnot_cost()
    data["initial_method"] = "m_flow" if enable_m_flow else "n_flow"
    data["n_qubits"] = n
    data["m_state"] = m
    data["n_g2_initial"] = n_cnot
    data["n_g_initial"] = len(circuit.get_gates()) - n_cnot
    data["time_initial"] = timer_old.time()
    state_vector_act = simulate_circuit(circuit)
    assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    return circuit

def run_ours(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    with stopwatch("resynthesis") as timer_new:
        new_circuit = resynthesis(circuit)
    n_cnot_new = new_circuit.get_cnot_cost()
    data["n_g2_ours"] = n_cnot_new
    data["n_g_ours"] = len(new_circuit.get_gates()) - n_cnot_new
    data["time_ours"] = timer_new.time()
    state_vector_act = simulate_circuit(new_circuit)
    assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    return new_circuit

def run_date24(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    with stopwatch("resynthesis") as timer_new:
        # DATE24
        new_circuit = prepare_state(state_vector, map_gates=True, verbose_level=0)
    n_cnot_new = new_circuit.get_cnot_cost()
    data["n_g2_date24"] = n_cnot_new
    data["n_g_date24"] = len(new_circuit.get_gates()) - n_cnot_new
    data["time_date24"] = timer_new.time()
    state_vector_act = simulate_circuit(new_circuit)
    assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    return new_circuit

import pyzx as zx
from pyzx.circuit import Circuit
def run_pyzx(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    # run the pyzx
    write_qasm(circuit, "/tmp/temp.qasm")
    c_zx = Circuit.load("/tmp/temp.qasm")
    with stopwatch("to_pyzx") as timer_pyzx:
        g = c_zx.to_graph()
        g = zx.simplify.teleport_reduce(g)
        c = zx.Circuit.from_graph(g).split_phase_gates()
        c = zx.optimize.basic_optimization(c).to_basic_gates().split_phase_gates()

    assert zx.compare_tensors(c, c_zx)
    n_cnot_pyzx = c.stats_dict()["twoqubit"]
    data["n_g2_pyzx"] = n_cnot_pyzx
    data["n_g_pyzx"] = c.stats_dict()["gates"] - n_cnot_pyzx
    data["time_pyzx"] = timer_pyzx.time()
    
    # with open("/tmp/temp_opt.qasm", "w") as f:
    #     f.write(c.to_qasm())
    # new_circuit = read_qasm("/tmp/temp_opt.qasm")
    # state_vector_act = simulate_circuit(new_circuit)
    # assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    # return new_circuit

def run_pyzx_ga(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    # run the pyzx
    write_qasm(circuit, "/tmp/temp.qasm")
    c_zx = Circuit.load("/tmp/temp.qasm")
    with stopwatch("to_pyzx") as timer_pyzx:
        ga_opt = zx.GeneticOptimizer()
        g_simp = c_zx.to_graph()
        g_evolve = ga_opt.evolve(g_simp, n_mutants=20, n_generations=100, quiet=False)
        zx.full_reduce(g_evolve)
        c_evolve = zx.extract_circuit(g_evolve.copy()).to_basic_gates()
        c_evolve = zx.basic_optimization(c_evolve)

    # this cannot pass the cec
    # assert zx.compare_tensors(c_evolve, c_zx)
    n_cnot_pyzx = c_evolve.stats_dict()["twoqubit"]
    data["n_g2_pyzx_ga"] = n_cnot_pyzx
    data["n_g_pyzx_ga"] = c_evolve.stats_dict()["gates"] - n_cnot_pyzx
    data["time_pyzx_ga"] = timer_pyzx.time()
    
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit import qasm2, transpile

def run_qiskit(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    n_qubits = circuit.get_num_qubits()
    backend = GenericBackendV2(num_qubits=n_qubits)
    pass_manager = generate_preset_pass_manager(optimization_level=3, backend=backend, basis_gates=["cx", "ry", "z"])
    qc = to_qiskit(circuit)
    with stopwatch("qiskit") as timer_qiskit:
        qc_opt = pass_manager.run(qc)
    # print(qc_opt.count_ops())
    # print(qc_opt)
    # print()
    n_total = sum(qc_opt.count_ops().values())
    data["n_g2_qiskit"] = qc_opt.count_ops().get("cx", 0)
    data["n_g_qiskit"] = n_total - data["n_g2_qiskit"]
    data["time_qiskit"] = timer_qiskit.time()
    
    return qc_opt
    
def get_benchmarks():
    
    benchmarks = []
    # W state
    for n_qubits in range(3, 12, 3):
        state_vector = W_state(n_qubits)
        benchmarks.append(("W", state_vector))
        
    # Dicke states
    for n_qubits in range(3, 8, 1):
        state_vector = D_state(n_qubits, n_qubits//2)
        benchmarks.append(("Dicke-Dense", state_vector))
    for n_qubits in range(3, 9, 1):
        state_vector = D_state(n_qubits, 2)
        benchmarks.append(("Dicke-Sparse", state_vector))
        
    # Cyclic states
    for n_qubits in range(3, 9, 1):
        state_vector = QBA_state(n_qubits, (2**(n_qubits-1))-1)
        benchmarks.append(("Cyclic-Sparse", state_vector))
    for n_qubits in range(3, 8, 1):
        state_vector = QBA_state(n_qubits, (2**(n_qubits-1))+1)
        benchmarks.append(("Cyclic-Dense", state_vector))

    # Random dense states
    for n_qubits in range(3, 8, 1):
        state_vector = rand_state(n_qubits, 2**(n_qubits-1), uniform=True)
        benchmarks.append(("Random-Dense-Uniform", state_vector))
    
    for n_qubits in range(3, 8, 1):
        state_vector = rand_state(n_qubits, 2**(n_qubits-1), uniform=False)
        benchmarks.append(("Random-Dense-Nonuniform", state_vector))
    
    # Random sparse states
    for n_qubits in range(3, 12, 1):
        state_vector = rand_state(n_qubits, n_qubits, uniform=True)
        benchmarks.append(("Random-Sparse-Uniform", state_vector))
        
    for n_qubits in range(3, 12, 1):
        state_vector = rand_state(n_qubits, n_qubits, uniform=False)
        benchmarks.append(("Random-Sparse-Nonuniform", state_vector))

    return benchmarks
    
if __name__ == "__main__":
    N_TESTS = 1

    datas = []

    for name, state_vector in get_benchmarks():
        data = {"name": name}
        circuit = generate_initial_circuit(state_vector, data)
        # print(to_qiskit(circuit))
        new_circuit_ours = run_ours(circuit, state_vector, data)
        new_circuit_pyzx = run_pyzx(circuit, state_vector, data)
        # new_circuit_pyzx_ga = run_pyzx_ga(circuit, state_vector, data)
        new_circuit_date24 = run_date24(circuit, state_vector, data)
        new_circuit_qiskit = run_qiskit(circuit, state_vector, data)

        datas.append(data)

        df = pd.DataFrame(datas)
        df.to_csv("resynthesis.csv")
