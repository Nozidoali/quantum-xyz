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
    QBA_state,
)
from xyz import StatePreparationParameters as Param

import pandas as pd

REPORT_TIME = True
REPORT_G = False
WRITE_FILES = True
N_LIST = list(range(3, 10, 3))
# N_LIST = list(range(11,20))
REPEAT = 10

REPORT_FIDELITY = True

def evaluate_fidelity(state_vector: np.ndarray, circuit: QCircuit) -> float:
    from qiskit_aer.noise import NoiseModel
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    from qiskit.quantum_info import Statevector, state_fidelity, DensityMatrix  

    
    from qiskit.providers.fake_provider import Fake27QPulseV1
    backend = Fake27QPulseV1()
    noise_model = NoiseModel.from_backend(backend)
    # Get coupling map from backend
    coupling_map = backend.configuration().coupling_map
    # Get basis gates from noise model
    basis_gates = noise_model.basis_gates

    sim_statevector = AerSimulator(
        method="density_matrix",
        noise_model=noise_model,
    )
    
    if isinstance(circuit, QCircuit):
        qc = to_qiskit(circuit, with_measurement=False)
    else:
        qc = circuit
    
    qc.save_density_matrix()
    # qc.save_statevector()
    
    transpiled_circuit = transpile(qc, backend=sim_statevector, optimization_level=3)
    result = sim_statevector.run(transpiled_circuit, shots=4096).result()
    density_matrix_act = result.data()["density_matrix"]
    
    state_exp = Statevector(state_vector)
    density_matrix_exp = DensityMatrix(state_exp)
    # state_act = Statevector(statevector)
    return state_fidelity(density_matrix_exp, density_matrix_act)

def generate_initial_circuit(state_vector: np.ndarray, data={}) -> QCircuit:
    # synthesize the state using the best method
    state = quantize_state(state_vector)
    n = state.num_qubits
    m = len(state.index_set)
    state_vector.dump(f"qsp_dataset/{name}_{n}_{m}.pkl")
    with open(f"qsp_dataset/{name}_{n}_{m}.txt", "w") as f:
        f.write(str(quantize_state(state_vector)))
    print(f"Generating initial circuit for qsp_dataset/{name}_{n}_{m}.pkl")
    enable_m_flow: bool = m * n < (1 << n)
    # enable_m_flow: bool = True
    enable_n_flow: bool = ~enable_m_flow
    param = Param(
        enable_compression=False,
        enable_m_flow=enable_m_flow,
        enable_n_flow=enable_n_flow,
        enable_exact_synthesis=False,
    )
    with stopwatch("synthesis") as timer_old:
        circuit = prepare_state(state, map_gates=True, verbose_level=0, param=param)
    n_cnot = circuit.get_cnot_cost()
    data["initial_method"] = "m_flow" if enable_m_flow else "n_flow"
    data["n_qubits"] = n
    data["m_state"] = m
    data["n_g2_initial"] = n_cnot
    if REPORT_FIDELITY:
        with stopwatch("fidelity") as timer_fidelity:
            data["fidelity_initial"] = evaluate_fidelity(state_vector, circuit)
        data["time_fidelity_initial"] = timer_fidelity.time()
    if REPORT_G:
        data["n_g_initial"] = len(circuit.get_gates()) - n_cnot
    if REPORT_TIME:
        data["time_initial"] = timer_old.time()
    state_vector_act = simulate_circuit(circuit)
    assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    if WRITE_FILES:
        write_qasm(circuit, f"qsp_dataset/{name}_{n}_{m}.init.qasm")
        print(f"Initial circuit saved to qsp_dataset/{name}_{n}_{m}.init.qasm")
    return circuit


def run_ours(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
    with stopwatch("resynthesis") as timer_new:
        new_circuit = resynthesis(circuit)
    n_cnot_new = new_circuit.get_cnot_cost()
    data["n_g2_ours"] = n_cnot_new
    if REPORT_FIDELITY:
        with stopwatch("fidelity") as timer_fidelity:
            data["fidelity_ours"] = evaluate_fidelity(state_vector, new_circuit)
        data["time_fidelity_ours"] = timer_fidelity.time()
    if REPORT_G:
        data["n_g_ours"] = len(new_circuit.get_gates()) - n_cnot_new
    if REPORT_TIME:
        data["time_ours"] = timer_new.time()
    with stopwatch("simulation") as timer_sim:
        state_vector_act = simulate_circuit(new_circuit)
        assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    data["time_sim"] = timer_sim.time()
    n, m = data["n_qubits"], data["m_state"]
    if WRITE_FILES:
        write_qasm(new_circuit, f"qsp_dataset/{name}_{n}_{m}.iccad24.qasm")
        print(f"Initial circuit saved to qsp_dataset/{name}_{n}_{m}.iccad24.qasm")
    return new_circuit


def run_date24(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
    with stopwatch("resynthesis") as timer_new:
        # DATE24
        new_circuit = prepare_state(state_vector, map_gates=True, verbose_level=0)
    n_cnot_new = new_circuit.get_cnot_cost()
    data["n_g2_date24"] = n_cnot_new
    if REPORT_FIDELITY:
        with stopwatch("fidelity") as timer_fidelity:
            data["fidelity_date24"] = evaluate_fidelity(state_vector, new_circuit)
        data["time_fidelity_date24"] = timer_fidelity.time()
    if REPORT_G:
        data["n_g_date24"] = len(new_circuit.get_gates()) - n_cnot_new
    if REPORT_TIME:
        data["time_date24"] = timer_new.time()
    state_vector_act = simulate_circuit(new_circuit)
    assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    n, m = data["n_qubits"], data["m_state"]
    write_qasm(new_circuit, f"qsp_dataset/{name}_{n}_{m}.data24.qasm")
    print(f"Initial circuit saved to qsp_dataset/{name}_{n}_{m}.date24.qasm")
    return new_circuit


def run_pyzx(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
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
    if REPORT_G:
        data["n_g_pyzx"] = c.stats_dict()["gates"] - n_cnot_pyzx
    if REPORT_TIME:
        data["time_pyzx"] = timer_pyzx.time()

    # with open("/tmp/temp_opt.qasm", "w") as f:
    #     f.write(c.to_qasm())
    # new_circuit = read_qasm("/tmp/temp_opt.qasm")
    # state_vector_act = simulate_circuit(new_circuit)
    # assert np.linalg.norm(state_vector_act - state_vector) < 1e-6
    # return new_circuit


def run_pyzx_ga(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
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


def run_qiskit(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit.transpiler import passes
    from qiskit.providers.fake_provider import GenericBackendV2
    from qiskit import qasm2, transpile
    from qiskit.quantum_info import Statevector, state_fidelity

    from qiskit.providers.fake_provider import Fake27QPulseV1

    n_qubits = circuit.get_num_qubits()
    backend = GenericBackendV2(num_qubits=n_qubits)
    
    pass_manager = generate_preset_pass_manager(
        optimization_level=3, backend=backend, basis_gates=["cx", "ry", "z"], 
        coupling_map=None,  # No coupling map for disabling qubit mapping
        initial_layout=None,  # No initial layout
        layout_method=None,  # No layout method
        routing_method=None,  # No routing method
        approximation_degree=1.0,
    )

    qc = to_qiskit(circuit)
    with stopwatch("qiskit") as timer_qiskit:
        qc_opt = pass_manager.run(qc)
    
    state_vector_act = Statevector(qc_opt)
    # state_vector_exp = Statevector(state_vector)
    # assert state_fidelity(state_vector_exp, state_vector_act) > 0.99, f"{state_fidelity(state_vector_exp, state_vector_act)}, {state_vector_exp}, {state_vector_act}"
    # print(qc_opt.count_ops())
    # print(qc_opt)
    # print()
    n_total = sum(qc_opt.count_ops().values())
    data["n_g2_qiskit"] = qc_opt.count_ops().get("cx", 0)
    if REPORT_FIDELITY:
        with stopwatch("fidelity") as timer_fidelity:
            data["fidelity_qiskit"] = evaluate_fidelity(state_vector_act.data, qc_opt)
        data["time_fidelity_qiskit"] = timer_fidelity.time()
    if REPORT_G:
        data["n_g_qiskit"] = n_total - data["n_g2_qiskit"]
    if REPORT_TIME:
        data["time_qiskit"] = timer_qiskit.time()

    return qc_opt


def run_bqskit(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
    from bqskit import compile
    from bqskit.qis import StateVector
    from bqskit.qis import StateSystem
    from bqskit.ext.qiskit import bqskit_to_qiskit
    from bqskit.ir.lang.qasm2 import OPENQASM2Language

    n, m = data["n_qubits"], data["m_state"]
    in1 = StateVector(ground_state(n))
    out1 = StateVector(state_vector)
    system = StateSystem({in1: out1})
    with stopwatch("bqskit") as timer_bqskit:
        c = compile(system, optimization_level=3)

    qc_opt = bqskit_to_qiskit(c)
    n_total = sum(qc_opt.count_ops().values())
    data["n_g2_bqskit"] = qc_opt.count_ops().get("cx", 0)
    if REPORT_FIDELITY:
        with stopwatch("fidelity") as timer_fidelity:
            data["fidelity_bqskit"] = evaluate_fidelity(state_vector, qc_opt)
        data["time_fidelity_bqskit"] = timer_fidelity.time()
    if REPORT_G:
        data["n_g_bqskit"] = n_total - data["n_g2_bqskit"]
    if REPORT_TIME:
        data["time_bqskit"] = timer_bqskit.time()
    with open(f"qsp_dataset/{name}_{n}_{m}.bqskit.qasm", "w") as f:
        f.write(OPENQASM2Language().encode(c))


def run_bqskit_flow(circuit: QCircuit, state_vector: np.ndarray, data={}) -> QCircuit:
    from bqskit.compiler import Workflow
    from bqskit.passes import (
        QuickPartitioner,
        ForEachBlockPass,
        ScanningGateRemovalPass,
        UnfoldPass,
        QSearchSynthesisPass,
    )

    basic_gate_deletion_workflow = Workflow(
        [
            QuickPartitioner(3),  # Partition into 3-qubit blocks
            ForEachBlockPass(
                ScanningGateRemovalPass()
            ),  # Apply gate deletion to each block (in parallel)
            UnfoldPass(),  # Unfold the blocks back into the original circuit
        ]
    )

    workflow = [
        QuickPartitioner(),
        ForEachBlockPass([QSearchSynthesisPass(), ScanningGateRemovalPass()]),
        UnfoldPass(),
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
    if REPORT_FIDELITY:
        with stopwatch("fidelity") as timer_fidelity:
            data["fidelity_bqskit_flow"] = evaluate_fidelity(state_vector, qc_opt)
        data["time_fidelity_bqskit_flow"] = timer_fidelity.time()
    if REPORT_G:
        data["n_g_bqskit_flow"] = n_total - data["n_g2_bqskit_flow"]
    if REPORT_TIME:
        data["time_bqskit_flow"] = timer_bqskit.time()


def get_benchmarks():
    benchmarks = []

    # W state
    for n_qubits in N_LIST:
        state_vector = W_state(n_qubits)
        benchmarks.append(("W", state_vector))

    # Dicke states
    for n_qubits in N_LIST:
        state_vector = D_state(n_qubits, n_qubits // 2)
        benchmarks.append(("Dicke", state_vector))

    # QBA states
    for n_qubits in N_LIST:
        state_vector = QBA_state(n_qubits, (2 ** (n_qubits - 1)) + 1)
        benchmarks.append(("QBA-Dense", state_vector))

    for _ in range(REPEAT):
        # Random dense states
        for n_qubits in N_LIST:
            state_vector = rand_state(n_qubits, 2 ** (n_qubits - 1), uniform=True)
            benchmarks.append(("Random-Dense-Uniform", state_vector))

        for n_qubits in N_LIST:
            state_vector = rand_state(n_qubits, 2 ** (n_qubits - 1), uniform=False)
            benchmarks.append(("Random-Dense-Nonuniform", state_vector))

        # Random sparse states
        for n_qubits in N_LIST:
            state_vector = rand_state(n_qubits, n_qubits, uniform=True)
            benchmarks.append(("Random-Sparse-Uniform", state_vector))

        for n_qubits in N_LIST:
            state_vector = rand_state(n_qubits, n_qubits, uniform=False)
            benchmarks.append(("Random-Sparse-Nonuniform", state_vector))

    return benchmarks


import xyz
from qiskit.quantum_info import Statevector

if __name__ == "__main__":
    N_TESTS = 1

    datas = []

    for name, state_vector in get_benchmarks():
        state_vector: np.ndarray
        data = {"name": name}
        try:
            # circuit = xyz.run_qclib(state_vector)
            circuit = generate_initial_circuit(state_vector, data)
            # print(to_qiskit(circuit))
            # circuit = run_date24(circuit, state_vector, data)
            # print(to_qiskit(circuit))
            # new_circuit_pyzx = run_pyzx(circuit, state_vector, data)
            # new_circuit_pyzx_ga = run_pyzx_ga(circuit, state_vector, data)
            new_circuit_qiskit = run_qiskit(circuit, state_vector, data)
            # new_circuit_bqskit = run_bqskit(circuit, state_vector, data)
            new_circuit_bqskit = run_bqskit_flow(circuit, state_vector, data)
            new_circuit_ours = run_ours(circuit, state_vector, data)
            # print(to_qiskit(new_circuit_ours))
        except AssertionError:
            print(f"state vector: {quantize_state(state_vector)}")
            print("Initial circuit")
            print(to_qiskit(circuit))
            print("Errornous circuit")
            print(new_circuit_qiskit)
            state_exp = simulate_circuit(circuit)
            state_act = Statevector(new_circuit_qiskit).data
            print(f"expect: {quantize_state(state_exp)}")
            print(f"actual: {quantize_state(state_act)}")
        datas.append(data)

        df = pd.DataFrame(datas)
        df.to_csv("resynthesis.csv")
