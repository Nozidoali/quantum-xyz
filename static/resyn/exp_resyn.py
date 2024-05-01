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
    ground_state,
    QBA_state
)
from xyz import StatePreparationParameters as Param

import pandas as pd

def generate_initial_circuit(state_vector: np.ndarray, data = {}) -> QCircuit:
    # synthesize the state using the best method
    state = quantize_state(state_vector)
    n = state.num_qubits
    m = len(state.index_set)
    state_vector.dump(f"qsp_dataset/{name}_{n}_{m}.pkl")
    with open(f"qsp_dataset/{name}_{n}_{m}.txt", "w") as f:
        f.write(str(quantize_state(state_vector)))
    print(f"Generating initial circuit for qsp_dataset/{name}_{n}_{m}.pkl")
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
    write_qasm(circuit, f"qsp_dataset/{name}_{n}_{m}.init.qasm")
    print(f"Initial circuit saved to qsp_dataset/{name}_{n}_{m}.init.qasm")
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
    n, m = data["n_qubits"], data["m_state"]
    write_qasm(new_circuit, f"qsp_dataset/{name}_{n}_{m}.iccad24.qasm")
    print(f"Initial circuit saved to qsp_dataset/{name}_{n}_{m}.iccad24.qasm")
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
    n, m = data["n_qubits"], data["m_state"]
    write_qasm(new_circuit, f"qsp_dataset/{name}_{n}_{m}.data24.qasm")
    print(f"Initial circuit saved to qsp_dataset/{name}_{n}_{m}.date24.qasm")
    return new_circuit

def run_pyzx(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    import pyzx as zx
    from pyzx.circuit import Circuit
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
    

def run_qiskit(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit.providers.fake_provider import GenericBackendV2
    from qiskit import qasm2, transpile
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

def run_bqskit(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    from bqskit import compile 
    from bqskit.qis import StateVector 
    from bqskit.qis import StateSystem 
    from bqskit.ext.qiskit import bqskit_to_qiskit
    from bqskit.ir.lang.qasm2 import OPENQASM2Language

    n, m = data["n_qubits"], data["m_state"]
    in1 = StateVector(ground_state(n))
    out1 = StateVector(state_vector) 
    system = StateSystem({in1:out1})
    with stopwatch("bqskit") as timer_bqskit:
        c = compile(system, optimization_level=3)
        
    qc_opt = bqskit_to_qiskit(c)
    n_total = sum(qc_opt.count_ops().values())
    data["n_g2_bqskit"] = qc_opt.count_ops().get("cx", 0)
    data["n_g_bqskit"] = n_total - data["n_g2_bqskit"]
    data["time_bqskit"] = timer_bqskit.time()
    with open(f"qsp_dataset/{name}_{n}_{m}.bqskit.qasm", "w") as f:
        f.write(OPENQASM2Language().encode(c))
    
def run_bqskit_flow(circuit: QCircuit, state_vector: np.ndarray, data = {}) -> QCircuit:
    from bqskit.compiler import Workflow
    from bqskit.passes import QuickPartitioner, ForEachBlockPass, ScanningGateRemovalPass, UnfoldPass, QSearchSynthesisPass

    basic_gate_deletion_workflow = Workflow([
        QuickPartitioner(3),  # Partition into 3-qubit blocks
        ForEachBlockPass(ScanningGateRemovalPass()),  # Apply gate deletion to each block (in parallel)
        UnfoldPass(),  # Unfold the blocks back into the original circuit
    ])
    
    workflow = [
        QuickPartitioner(),
        ForEachBlockPass([
            QSearchSynthesisPass(),
            ScanningGateRemovalPass()
        ]),
        UnfoldPass()
    ]
    
    from bqskit.compiler import Compiler
    from bqskit.ext.qiskit import bqskit_to_qiskit, qiskit_to_bqskit

    qc = to_qiskit(circuit)
    with stopwatch("bqskit_flow") as timer_bqskit:
        with Compiler() as compiler:
            # opt_circuit = compiler.compile(qiskit_to_bqskit(qc), workflow=basic_gate_deletion_workflow)
            opt_circuit = compiler.compile(qiskit_to_bqskit(qc), workflow=workflow)

    qc_opt = bqskit_to_qiskit(opt_circuit)
    n_total = sum(qc_opt.count_ops().values())
    data["n_g2_bqskit_flow"] = qc_opt.count_ops().get("cx", 0)
    data["n_g_bqskit_flow"] = n_total - data["n_g2_bqskit_flow"]
    data["time_bqskit_flow"] = timer_bqskit.time()

def get_benchmarks():
    
    benchmarks = []

    # W state
    for n_qubits in range(3, 13, 3):
        state_vector = W_state(n_qubits)
        benchmarks.append(("W", state_vector))
        
    # Dicke states
    for n_qubits in range(3, 13, 3):
        state_vector = D_state(n_qubits, n_qubits//2)
        benchmarks.append(("Dicke-Dense", state_vector))
    for n_qubits in range(3, 13, 3):
        state_vector = D_state(n_qubits, 2)
        benchmarks.append(("Dicke-Sparse", state_vector))
        
    # QBA states
    for n_qubits in range(3, 13, 3):
        state_vector = QBA_state(n_qubits, (2**(n_qubits-1))-1)
        benchmarks.append(("QBA-Sparse", state_vector))
    for n_qubits in range(3, 13, 3):
        state_vector = QBA_state(n_qubits, (2**(n_qubits-1))+1)
        benchmarks.append(("QBA-Dense", state_vector))

    # Random dense states
    for n_qubits in range(4, 13, 3):
        state_vector = rand_state(n_qubits, 2**(n_qubits-1), uniform=True)
        benchmarks.append(("Random-Dense-Uniform", state_vector))
    
    for n_qubits in range(4, 13, 3):
        state_vector = rand_state(n_qubits, 2**(n_qubits-1), uniform=False)
        benchmarks.append(("Random-Dense-Nonuniform", state_vector))
    
    # Random sparse states
    for n_qubits in range(4, 13, 3):
        state_vector = rand_state(n_qubits, n_qubits, uniform=True)
        benchmarks.append(("Random-Sparse-Uniform", state_vector))
        
    for n_qubits in range(4, 13, 3):
        state_vector = rand_state(n_qubits, n_qubits, uniform=False)
        benchmarks.append(("Random-Sparse-Nonuniform", state_vector))

    return benchmarks
    
if __name__ == "__main__":
    N_TESTS = 1

    datas = []

    for name, state_vector in get_benchmarks():
        state_vector: np.ndarray
        data = {"name": name}
        try:
            circuit = generate_initial_circuit(state_vector, data)
            # print(to_qiskit(circuit))
            new_circuit_ours = run_ours(circuit, state_vector, data)
            # new_circuit_pyzx = run_pyzx(circuit, state_vector, data)
            # new_circuit_pyzx_ga = run_pyzx_ga(circuit, state_vector, data)
            # new_circuit_date24 = run_date24(circuit, state_vector, data)
            # new_circuit_qiskit = run_qiskit(circuit, state_vector, data)
            # new_circuit_bqskit = run_bqskit(circuit, state_vector, data)
            # new_circuit_bqskit = run_bqskit_flow(circuit, state_vector, data)
        except AssertionError:            
            print("Initial circuit")
            print(to_qiskit(circuit))
            print("Errornous circuit")
            print(to_qiskit(new_circuit_ours))
            state_exp = simulate_circuit(circuit)
            state_act = simulate_circuit(new_circuit_ours)
            print(f"expect: {quantize_state(state_exp)}")
            print(f"actual: {quantize_state(state_act)}")
        datas.append(data)

        df = pd.DataFrame(datas)
        df.to_csv("resynthesis.csv")
