#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-06-19 12:06:15
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 13:43:10
'''

import numpy as np
from Circuit import QCircuit
from Util import *
from .Decompose import *

class PivotQubitPair:

    def __init__(self, tt: np.ndarray, index: int) -> None:
        self.tt = tt
        self.index = index

def get_gibbs(on: np.ndarray, off: np.ndarray) -> float:
    
    def p(x: float) -> float:
        return x * x * np.log2(x) if x != 0 else 0

    x = np.count_nonzero(on)
    y = np.count_nonzero(off)

    return p(x + y) - p(x) - p(y)

def select_pivot_qubit(on_set: np.ndarray, off_set: np.ndarray, qubits) -> int:

    num_qubits = len(qubits)

    print("on_set: ", on_set)
    print("off_set: ", off_set)
    
    best_gibbs = get_gibbs(on_set, off_set)
    best_qubit = None

    for qubit in qubits:
        tt = qubit.tt
        index = qubit.index

        curr_gibbs = get_gibbs(on_set & tt, off_set & tt) + get_gibbs(on_set & (~tt), off_set & (~tt))

        if curr_gibbs < best_gibbs:
            best_gibbs = curr_gibbs
            best_qubit = qubit

    return best_qubit, best_gibbs

def get_decision_tree_from_state_helper(on_set: np.array, off_set: np.array, qubits, decision_tree: DecisionTree) -> DecisionTree:

    if np.count_nonzero(on_set == 1) == 0:
        return decision_tree.const0
    if np.count_nonzero(off_set == 1) == 0:
        return decision_tree.const1

    best_qubit, _ = select_pivot_qubit(on_set, off_set, qubits)

    tt = best_qubit.tt
    index = best_qubit.index

    leaf1 = get_decision_tree_from_state_helper(on_set & tt, off_set & tt, qubits, decision_tree)
    leaf0 = get_decision_tree_from_state_helper(on_set & (~tt), off_set & (~tt), qubits, decision_tree)

    node = DecisionTreeNode()
    node.left_node = leaf0
    node.right_node = leaf1
    node.pivot_index = index

    return node
    
def get_decision_tree_from_state(matrix: np.array) -> DecisionTree:

    dt = DecisionTree()

    on_set = matrix.copy()
    off_set = 1 - matrix


    num_qubits = int(np.log2(matrix.shape[0]))

    basis_vector = np.array([1,1])
    non_basis_vector = np.array([1,0])

    pivot_qubits = []

    # TODO: move this to Truthtable Utils
    for i in range(num_qubits):
        tt = np.array([1]) # base
        for j in range(num_qubits):
            if j == i:
                tt = np.kron(tt, non_basis_vector)
            else:
                tt = np.kron(tt, basis_vector)

        pivot_qubit = PivotQubitPair(tt, i)
        pivot_qubits.append(pivot_qubit)

    root_node = get_decision_tree_from_state_helper(on_set, off_set, pivot_qubits, dt)

    dt.root = root_node
    
    return dt

def get_rotation_Y_theta(ratio: float):

    # G(P) = RY(2arccos(sqrt(P)))
    # where G(P) Ket(0) = sqrt(P) Ket(0) + sqrt(1 - P(0)) Ket(1)
    return 2 * np.arccos(np.sqrt(ratio))

def retrieve_circuit_from_decision_tree_helper(decision_tree: DecisionTree, decision_tree_node: DecisionTreeNode, circuit: QCircuit, current_controls: list) -> None:

    # first we create the ry gates
    ratio = decision_tree_node.pivot_value
    index = decision_tree_node.pivot_index
    theta = get_rotation_Y_theta(ratio)

    # this ry is controlled by the current controls
    # circuit.ry(theta, circuit.qr[index])

    # we need to derive the multi-controlled ry gate
    control_qubits = {qubit_index: phase for qubit_index, phase in current_controls}
    unitary_matrix = AdvancedGate.mcry(theta, control_qubits, circuit.num_qubits)

    decompose_multiple_controlled_rotation_Y_gate(unitary_matrix, circuit, control_qubits.keys())


def retrieve_circuit_from_decision_tree(decision_tree: DecisionTree, num_qubits: int) -> QCircuit:

    circuit = QCircuit(num_qubits)

    

    circuit.flush()
    circuit.measure()
    
    return circuit


def cofactor_decomposition(matrix: np.ndarray) -> QCircuit:
    """
    Returns the Cofactor decomposition
    """

    dt = get_decision_tree_from_state(matrix)

    num_qubits = int(np.log2(matrix.shape[0]))
    
    circuit = retrieve_circuit_from_decision_tre(dt, num_qubits)

    return circuit