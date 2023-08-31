#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 13:20:14
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 14:11:44
"""

from xyz.boolean import TruthTable

from xyz.srgraph import QState


def _qubit_reduction_impl(state: QState, target_qubit: int, final_qubit: int):
    """Perform a qubit reduction on the circuit .

    :param circuit: [description]
    :type circuit: [type]
    :param state: [description]
    :type state: QState
    :param target_qubit: [description]
    :type target_qubit: int
    """

    truth_table = TruthTable(state.num_qubits)

    for index in state.index_set:
        reversed_index = index ^ (1 << target_qubit)
        assert reversed_index not in state.index_set

        target_val = index >> target_qubit & 1
        final_val = index >> final_qubit & 1

        truth_table.set_bit(reversed_index, target_val ^ final_val)
        truth_table.set_bit(index, target_val ^ final_val)

    print(f"initial = {target_qubit}, final = {final_qubit}, tt = {truth_table}")


def qubit_reduction(circuit, state: QState):
    """Reduce the number of qubit in a circuit .

    :param circuit: [description]
    :type circuit: [type]
    :param qubit_map: [description]
    :type qubit_map: [type]
    :return: [description]
    :rtype: [type]
    """

    for qubit in range(state.num_qubits):
        for final_qubit in range(state.num_qubits):
            if qubit == final_qubit:
                continue
            _qubit_reduction_impl(state, qubit, final_qubit)

    print(f"state = {state}")
