#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 11:52:40
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 14:36:42
"""

import xyz
import pyzx as zx
from pyzx.circuit import Circuit
import matplotlib.pyplot as plt

if __name__ == "__main__":
    qc = xyz.read_qasm("./dicke_3.qasm")
    n_cnots = qc.get_cnot_cost()
    print(f"Original CNOT cost: {n_cnots}")

    qc_opt = xyz.resynthesis(qc)
    xyz.write_qasm(qc_opt, "./dicke_3_opt.qasm")
    n_cnots_opt = qc_opt.get_cnot_cost()
    print(f"Optimized CNOT cost: {n_cnots_opt}")

    c1 = Circuit.load("./dicke_3.qasm")
    c2 = Circuit.load("./dicke_3_opt.qasm")
    cec = zx.compare_tensors(c1, c2)
    print(cec)
    print(c1.stats())

    g = c1.to_graph()
    m = zx.draw_matplotlib(g)
    m.savefig("circuit.pdf")

    print(xyz.to_qiskit(qc_opt))

    g = zx.simplify.teleport_reduce(g)
    c = zx.Circuit.from_graph(g).split_phase_gates()
    c = zx.optimize.basic_optimization(c).to_basic_gates().split_phase_gates()
    cec = zx.compare_tensors(c, c1)
    print(cec)
    print(c.stats())

    g2 = c.to_graph()
    g2 = zx.simplify.teleport_reduce(g2)
    m = zx.draw_matplotlib(g2)
    m.savefig("circuit_opt.pdf")
    exit(0)

    ga_opt = zx.GeneticOptimizer()

    g_simp = c.to_graph()

    g_evolve = ga_opt.evolve(g_simp, n_mutants=20, n_generations=40, quiet=False)
    zx.full_reduce(g_evolve)
    c_evolve = zx.extract_circuit(g_evolve.copy()).to_basic_gates()
    c_evolve = zx.basic_optimization(c_evolve)
    print(c_evolve.stats())
