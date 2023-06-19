#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-19 12:06:15
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-19 21:43:13
"""

import numpy as np
from Circuit import QCircuit
from Utils import *
from .Decompose import *
from .Synthesis import *


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

        curr_gibbs = get_gibbs(on_set & tt, off_set & tt) + get_gibbs(
            on_set & (~tt), off_set & (~tt)
        )

        if curr_gibbs < best_gibbs:
            best_gibbs = curr_gibbs
            best_qubit = qubit

    return best_qubit, best_gibbs


def get_decision_tree_from_state_helper(
    on_set: np.array, off_set: np.array, qubits, decision_tree: DecisionTree
) -> DecisionTree:

    if np.count_nonzero(on_set == 1) == 0:
        return decision_tree.const0
    if np.count_nonzero(off_set == 1) == 0:
        return decision_tree.const1

    best_qubit, _ = select_pivot_qubit(on_set, off_set, qubits)

    tt = best_qubit.tt
    index = best_qubit.index

    leaf_positive = get_decision_tree_from_state_helper(
        on_set & tt, off_set & tt, qubits, decision_tree
    )
    leaf_negative = get_decision_tree_from_state_helper(
        on_set & (~tt), off_set & (~tt), qubits, decision_tree
    )

    node = DecisionTreeNode()
    node.negative_cofactor = leaf_negative
    node.positive_cofactor = leaf_positive
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

        assert np.isclose(i, weight), "The input matrix is not a uniform quantum state"
        normalized_matrix = np.append(normalized_matrix, 1)

    on_set = normalized_matrix.copy()
    off_set = 1 - on_set

    # print(f"on set = {on_set}")
    # print(f"off set = {off_set}")

    num_qubits = int(np.log2(matrix.shape[0]))

    basis_vector = np.array([1, 1])
    non_basis_vector = np.array([0, 1])

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

    root_node = get_decision_tree_from_state_helper(on_set, off_set, pivot_qubits, dt)

    dt.root = root_node

    return dt


def apply_control_sequence_to_y(
    circuit: QCircuit, control_sequence: list, control_qubits: list, target_qubit
) -> None:
    for control in control_sequence:
        rotation_theta, control_id = control

        circuit.ry(rotation_theta, target_qubit)
        circuit.cx(control_qubits[control_id], target_qubit)


def get_rotation_Y_theta(ratio: float):

    # G(P) = RY(2arccos(sqrt(P)))
    # where G(P) Ket(0) = sqrt(P) Ket(0) + sqrt(1 - P(0)) Ket(1)
    return 2 * np.arccos(np.sqrt(ratio))


from .ShannonDecomposition import *


def retrieve_circuit_from_decision_tree_helper(
    decision_tree: DecisionTree,
    decision_tree_node: DecisionTreeNode,
    circuit: QCircuit,
    current_controls: list,
) -> None:

    if decision_tree_node.is_leaf:
        return

    # first we create the ry gates
    ratio = decision_tree_node.pivot_value
    index = decision_tree_node.pivot_index

    theta = get_rotation_Y_theta(ratio)

    # we need to derive the multi-controlled ry gate
    # number of qubits = control_qubits + 1

    effective_theta = theta - 2 * np.pi * np.floor(theta / (2 * np.pi))
    if np.isclose(effective_theta, 0):
        effective_theta = 0

    else:
        print(
            f"theta = {effective_theta}, ratio = {ratio}, index = {index}, controls = {current_controls}"
        )

        if len(current_controls) == 0:
            circuit.ry(effective_theta, circuit.qr[index])

        else:

            # we prepare the rotation table
            rotation_table = np.zeros(2 ** (len(current_controls)))

            rotated_index = 0
            for i, value_tuple in enumerate(current_controls):
                _, controlled_by_one = value_tuple
                if controlled_by_one == True:
                    rotated_index += 2 ** i

            control_qubits = [
                circuit.qr[qubit_index] for qubit_index, _ in current_controls
            ]

            # only rotate the target qubit if the control qubits are in the positive phase
            rotation_table[rotated_index] = effective_theta

            # print(f"rotation table = {rotation_table}")
            # print(f"control qubits = {control_qubits}")

            control_sequence = synthesize_multi_controlled_rotations(rotation_table)
            print(f"control sequence = {control_sequence}")

            apply_control_sequence_to_y(
                circuit, control_sequence, control_qubits, circuit.qr[index]
            )

    # then we add the control singles to the current controls and start the recursion

    new_controls = current_controls.copy()

    # first the positive cofactor
    new_controls.append((index, True))
    retrieve_circuit_from_decision_tree_helper(
        decision_tree, decision_tree_node.positive_cofactor, circuit, new_controls
    )
    new_controls = new_controls[:-1]

    # then the negative cofactor
    new_controls.append((index, False))
    retrieve_circuit_from_decision_tree_helper(
        decision_tree, decision_tree_node.negative_cofactor, circuit, new_controls
    )
    new_controls = new_controls[:-1]


def retrieve_circuit_from_decision_tree(
    decision_tree: DecisionTree, num_qubits: int
) -> QCircuit:

    circuit = QCircuit(num_qubits)

    retrieve_circuit_from_decision_tree_helper(
        decision_tree, decision_tree.root, circuit, []
    )

    circuit.flush()
    circuit.measure()

    return circuit


import subprocess


def cofactor_decomposition(matrix: np.ndarray) -> QCircuit:
    """
    Returns the Cofactor decomposition
    """

    dt = get_decision_tree_from_state(matrix)

    dt.export("decision_tree.dot")
    subprocess.run(["dot", "-Tpng", "decision_tree.dot", "-o", "decision_tree.png"])

    num_qubits = int(np.log2(matrix.shape[0]))

    circuit = retrieve_circuit_from_decision_tree(dt, num_qubits)

    return circuit
