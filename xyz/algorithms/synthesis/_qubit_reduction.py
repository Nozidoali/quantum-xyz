#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 13:20:14
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 14:11:44
"""

import numpy as np


from xyz.boolean import TruthTable
from xyz.boolean.sum_of_product import sop_to_str, convert_tt_to_sop, sop_to_tt
from xyz.boolean.truth_table import (
    TruthTableEntry,
    const0_truth_table,
    const1_truth_table,
)
from xyz.circuit import MCRY, CX, RY, decompose_mcry, control_sequence_to_gates
from xyz.qstate import QState


def _get_flip_truth_table(
    state: QState,
    target_qubit: int,
    control_qubit: int,
    phase: bool,
    verbose: bool = False,
):
    """Get flip truth table .

    :param state: [description]
    :type state: QState
    :param target_qubit: [description]
    :type target_qubit: int
    :param control_qubit: [description]
    :type control_qubit: int
    :param phase: [description]
    :type phase: bool
    """
    truth_table = TruthTable(state.num_qubits)

    index_to_thetas = {}

    if verbose:
        print(
            f"target_qubit = {target_qubit}, control_qubit = {control_qubit}, phase = {phase}"
        )

    visited_index = set()
    for index in state.index_set:
        if index in visited_index:
            continue

        reversed_index = index ^ (1 << target_qubit)

        # we need to make sure that we have not visited the reversed index
        visited_index.add(index)
        visited_index.add(reversed_index)

        target_val = index >> target_qubit & 1
        final_val = (index >> control_qubit & 1) ^ phase ^ 1

        # for each index, we need to know what is the final index
        final_index = index & ~(1 << target_qubit)
        if final_val:
            final_index |= 1 << target_qubit

        if verbose:
            print(f"|{index:0{state.num_qubits}b}>: {target_val} -> {final_val}")

        # if to flip is 1, then we need to flip the target qubit
        # else if to flip is 0, then we need to make sure the target qubit is not flipped
        to_flip = target_val ^ final_val

        # the problem is simple if we already have one-to-one mapping
        if reversed_index not in state.index_set:
            truth_table.set_bit(reversed_index, to_flip)
            truth_table.set_bit(index, to_flip)

        else:
            # now we need to check if there is a conflict
            reversed_target_val = reversed_index >> target_qubit & 1
            reversed_final_val = (reversed_index >> control_qubit & 1) ^ phase ^ 1

            # if to flip is 1, then we need to flip the target qubit
            # else if to flip is 0, then we need to make sure the target qubit is not flipped
            reversed_to_flip = reversed_target_val ^ reversed_final_val
            assert reversed_to_flip != to_flip  # this should always be true

            index0 = index if not to_flip else reversed_index
            index1 = index if to_flip else reversed_index
            theta = 2 * np.arccos(
                np.sqrt(
                    state.index_to_weight[index0]
                    / (state.index_to_weight[index1] + state.index_to_weight[index0])
                )
            )

            index_to_thetas[index] = theta
            index_to_thetas[reversed_index] = theta

    return truth_table, index_to_thetas


def _reduce_qubit(state: QState, target_qubit: int, control_qubit: int, phase: bool):
    """Perform a qubit reduction on the circuit .

    :param circuit: [description]
    :type circuit: [type]
    :param state: [description]
    :type state: QState
    :param target_qubit: [description]
    :type target_qubit: int
    """

    truth_table, index_to_thetas = _get_flip_truth_table(
        state, target_qubit, control_qubit, phase
    )

    supports = state.get_supports()
    supports.remove(target_qubit)

    esop = None
    if truth_table == const0_truth_table(state.num_qubits):
        esop = []
    elif truth_table == const1_truth_table(state.num_qubits):
        raise ValueError("Cannot convert truth table to SOP")
    else:
        esop = convert_tt_to_sop(truth_table, supports)

    if esop is None:
        print(f"truth_table = {truth_table}")
        raise ValueError("Cannot convert truth table to SOP")

    # we evaluate the cost
    cost: int = 0
    for term in esop:
        term_cost = 1 << (len(term) - 1)
        cost += term_cost

    # then let us evaluate the rotation cost
    if len(index_to_thetas) > 0:
        truth_table_real = sop_to_tt(esop, state.num_qubits)

        # now we check the other index

        for index in index_to_thetas:
            if truth_table_real.get_bit(index) == TruthTableEntry.ONE:
                index_to_thetas[index] += np.pi

        for index in state.index_set:
            if index not in index_to_thetas:
                index_to_thetas[index] = 0
        supports = _get_rotation_supports(
            index_to_thetas, state.num_qubits, target_qubit
        )
        cost += 1 << (len(supports))
    return esop, index_to_thetas, cost


def _get_rotation_supports(index_to_theta: dict, num_lits: int, target_qubit: int):
    lit_to_val = {}
    supports = set()
    for index, _ in index_to_theta.items():
        for lit in range(num_lits):
            if lit == target_qubit:
                continue
            lit_val = (index >> lit) & 1
            if lit not in lit_to_val:
                lit_to_val[lit] = lit_val
            elif lit_to_val[lit] != lit_val:
                supports.add(lit)

    return supports


def _qubit_reduction_impl(
    circuit, state: QState, optimality_level: int = 1, verbose: bool = False
):
    """Reduce the number of qubit in a circuit .

    :param circuit: [description]
    :type circuit: [type]
    :param qubit_map: [description]
    :type qubit_map: [type]
    :return: [description]
    :rtype: [type]
    """

    # make greedy decision
    best_esop = None
    best_cost = None
    best_phase = None
    best_target_qubit = None
    best_control_qubit = None
    best_index_to_thetas = None
    supports = state.get_supports()

    search_done = False
    for qubit in supports:
        if search_done:
            break
        for control_qubit in supports:
            if search_done:
                break
            if qubit == control_qubit:
                continue
            for phase in [0, 1]:
                try:
                    esop, index_to_thetas, cost = _reduce_qubit(
                        state, qubit, control_qubit, phase
                    )
                    if best_esop is None or cost < best_cost:
                        best_esop = esop
                        best_cost = cost
                        best_target_qubit = qubit
                        best_control_qubit = control_qubit
                        best_phase = phase
                        best_index_to_thetas = index_to_thetas

                        if optimality_level <= 1:
                            search_done = True
                            break
                except ValueError:
                    continue

    assert best_esop is not None

    # debug
    if verbose:
        print(
            f"best_cost = {best_cost}, best_target_qubit = {best_target_qubit}, best_control_qubit = {best_control_qubit}, best_phase = {best_phase}, best_esop = {sop_to_str(best_esop)}"
        )

    # now we need to add gates
    gates = []

    # the first gate is a CX using final qubit to control the target qubit
    assert best_target_qubit != best_control_qubit
    gate = CX(
        circuit.qubit_at(best_control_qubit),
        best_phase,
        circuit.qubit_at(best_target_qubit),
    )
    gates.append(gate)

    # then depending on the rotation table, we need to add rotation gates
    if len(best_index_to_thetas) != 0:
        supports = list(
            _get_rotation_supports(
                best_index_to_thetas, state.num_qubits, best_target_qubit
            )
        )
        if len(supports) == 0:
            # we assert index_to_thetas has only one element
            assert len(best_index_to_thetas) == 1

            # get the theta
            theta = list(best_index_to_thetas.values())[0]

            # then we add a RY gate
            gates.append(RY(theta, circuit.qubit_at(best_target_qubit)))

        else:
            rotation_table = [0 for i in range(1 << len(supports))]
            for index, theta in best_index_to_thetas.items():
                # we need to find the rotation index
                rotation_index = 0
                for i, lit in enumerate(supports):
                    rotation_index |= ((index >> lit) & 1) << i
                rotation_table[rotation_index] = theta

            support_qubits = [circuit.qubit_at(lit) for lit in supports]
            target_qubit = circuit.qubit_at(best_target_qubit)
            assert best_target_qubit not in supports
            control_sequence = decompose_mcry(rotation_table)
            rotation_gates = control_sequence_to_gates(
                control_sequence, support_qubits, target_qubit
            )
            for gate in rotation_gates:
                gates.append(gate)

    target_qubit = circuit.qubit_at(best_target_qubit)
    for term in best_esop:
        # we need to decide which gate to add
        if len(term) == 1:
            lit = term[0]
            assert lit.lit != best_target_qubit
            control_qubit = circuit.qubit_at(lit.lit)
            control_phase = lit.phase
            # we need to add an X gate
            gate = CX(control_qubit, control_phase, target_qubit)
            gates.append(gate)

        else:
            # we need to add a Toffoli gate
            control_qubits = []
            control_phases = []
            for lit in term:
                assert lit.lit != best_target_qubit
                control_qubits.append(circuit.qubit_at(lit.lit))
                control_phases.append(lit.phase)
            gate = MCRY(np.pi, control_qubits, control_phases, target_qubit)
            gates.append(gate)

    # now we check the new state
    index_to_weight = {}
    for index, weight in state.index_to_weight.items():
        new_index = index & ~(1 << best_target_qubit)

        # final_val = (index >> best_control_qubit & 1) ^ best_phase ^ 1
        # new_index = new_index | (final_val << best_target_qubit)

        if new_index not in index_to_weight:
            index_to_weight[new_index] = 0

        index_to_weight[new_index] += weight

    new_state = QState(index_to_weight, state.num_qubits)

    return gates, new_state


def qubit_reduction(circuit, target_state: QState, optimality_level: int = 1):
    """Qubit reduction algorithm based on ESOP decomposition of a qubit.

    :param circuit: [description]
    :type circuit: [type]
    :param target_state: [description]
    :type target_state: QState
    :param optimality_level: [description], defaults to 1
    :type optimality_level: int, optional
    :return: [description]
    :rtype: [type]
    """

    all_gates = []
    # we stop searching for optimal solution if the number of supports is less than 5
    # we first try to qubit reduction
    num_supports = len(target_state.get_supports())
    while num_supports > 4:
        gates, new_state = _qubit_reduction_impl(
            circuit, target_state, optimality_level
        )
        for gate in gates[::-1]:
            all_gates.append(gate)
        target_state = new_state
        _num_supports = len(target_state.get_supports())
        assert _num_supports < num_supports
        num_supports = _num_supports

    return all_gates
