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

    # print("on_set: ", on_set)
    # print("off_set: ", off_set)

    best_gibbs = get_gibbs(on_set, off_set)
    best_qubit = None

    for qubit in qubits:
        tt = qubit.tt
        index = qubit.index

        curr_gibbs = get_gibbs(on_set & tt, off_set & tt) + \
            get_gibbs(on_set & (~tt), off_set & (~tt))

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

    leaf1 = get_decision_tree_from_state_helper(
        on_set & tt, off_set & tt, qubits, decision_tree)
    leaf0 = get_decision_tree_from_state_helper(
        on_set & (~tt), off_set & (~tt), qubits, decision_tree)

    node = DecisionTreeNode()
    node.negative_cofactor = leaf0
    node.positive_cofactor = leaf1
    node.pivot_index = index
    node.pivot_value = np.count_nonzero(on_set & (~tt)) / np.count_nonzero(on_set)
    
    return node


def get_decision_tree_from_state(matrix: np.array) -> DecisionTree:

    dt = DecisionTree()

    weight: float = None

    normalized_matrix = np.array([], dtype=bool)

    # we need to make sure it is a uniform quantum state
    for i in matrix:
        # skip the zeros
        if np.isclose(i, 0):
            normalized_matrix = np.append(normalized_matrix, 0)
            continue

        if weight is None:
            weight = i
            normalized_matrix = np.append(normalized_matrix, 1)
            continue

        assert np.isclose(
            i, weight), "The input matrix is not a uniform quantum state"
        normalized_matrix = np.append(normalized_matrix, 1)

    on_set = normalized_matrix.copy()
    off_set = 1 - on_set

    # print(f"on set = {on_set}")
    # print(f"off set = {off_set}")

    num_qubits = int(np.log2(matrix.shape[0]))

    basis_vector = np.array([1, 1])
    non_basis_vector = np.array([1, 0])

    pivot_qubits = []

    # TODO: move this to Truthtable Utils
    for i in range(num_qubits):
        tt = np.array([1])  # base
        for j in range(num_qubits):
            if j == i:
                tt = np.kron(tt, non_basis_vector)
            else:
                tt = np.kron(tt, basis_vector)

        pivot_qubit = PivotQubitPair(tt, i)
        pivot_qubits.append(pivot_qubit)

    root_node = get_decision_tree_from_state_helper(
        on_set, off_set, pivot_qubits, dt)

    dt.root = root_node

    return dt


def get_rotation_Y_theta(ratio: float):

    # G(P) = RY(2arccos(sqrt(P)))
    # where G(P) Ket(0) = sqrt(P) Ket(0) + sqrt(1 - P(0)) Ket(1)
    return 2 * np.arccos(np.sqrt(ratio))

from .ShannonDecomposition import *

def retrieve_circuit_from_decision_tree_helper(decision_tree: DecisionTree, decision_tree_node: DecisionTreeNode, circuit: QCircuit, current_controls: list) -> None:
    
    if decision_tree_node.is_leaf:
        return
    

    # first we create the ry gates
    ratio = decision_tree_node.pivot_value
    index = decision_tree_node.pivot_index
    
    theta = get_rotation_Y_theta(ratio)

    # we need to derive the multi-controlled ry gate
    # number of qubits = control_qubits + 1
    reindex_qubits: dict = {}
    for i, value_tuple in enumerate(current_controls):
        _, phase = value_tuple
        reindex_qubits[i+1] = phase

    print(f"adding ry gate to qubit {index} with ratio = {ratio}")
    print(f"current controls = {reindex_qubits}")
    unitary_matrix = AdvancedGate.mcry(
        theta, reindex_qubits, 0, len(current_controls) + 1)
    print(unitary_matrix)

    control_qubits = [circuit.qr[i] for i, _ in current_controls]
    assert circuit.qr[index] not in control_qubits
    all_qubits = control_qubits + [circuit.qr[index]]

    if True:
        quantum_shannon_decomposition_helper(unitary_matrix, circuit, all_qubits)
    if False:
        half = unitary_matrix.shape[0] // 2
        decompose_multiple_controlled_rotation_Y_gate(
            unitary_matrix[:half, half:], circuit, control_qubits, circuit.qr[index])

    # then we add the control singles to the current controls and start the recursion

    new_controls = current_controls.copy()
    
    # first the positive cofactor
    new_controls.append((index, True))
    retrieve_circuit_from_decision_tree_helper(
        decision_tree, decision_tree_node.positive_cofactor, circuit, new_controls)
    new_controls = new_controls[:-1]

    # then the negative cofactor
    new_controls.append((index, False))
    retrieve_circuit_from_decision_tree_helper(
        decision_tree, decision_tree_node.negative_cofactor, circuit, new_controls)
    new_controls = new_controls[:-1]


def retrieve_circuit_from_decision_tree(decision_tree: DecisionTree, num_qubits: int) -> QCircuit:

    circuit = QCircuit(num_qubits)

    retrieve_circuit_from_decision_tree_helper(
        decision_tree, decision_tree.root, circuit, [])

    circuit.flush()
    circuit.measure()

    return circuit


def cofactor_decomposition(matrix: np.ndarray) -> QCircuit:
    """
    Returns the Cofactor decomposition
    """

    dt = get_decision_tree_from_state(matrix)
    
    dt.export("decision_tree.dot")

    num_qubits = int(np.log2(matrix.shape[0]))

    circuit = retrieve_circuit_from_decision_tree(dt, num_qubits)

    return circuit
