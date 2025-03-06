#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 07:23:32
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 07:30:46
"""

import numpy as np
from xyz import MCRY, QBit, QState, quantize_state


def test_mcry_1():
    state = quantize_state([1, 1, 1, 1, 1, 1, 1, 1])
    gate = MCRY(
        theta=np.pi / 2,
        control_qubits=[QBit(1), QBit(2)],
        phases=[0, 0],
        target_qubit=QBit(0),
    )
    new_state = gate.apply(state)
    assert 0b000 not in new_state.index_set
    assert 0b001 in new_state.index_set
    assert 0b010 in new_state.index_set
    assert 0b011 in new_state.index_set
    assert 0b100 in new_state.index_set
    assert 0b101 in new_state.index_set
    assert 0b110 in new_state.index_set
    assert 0b111 in new_state.index_set
    assert np.isclose(new_state.index_to_weight[0b001], 0.5)


def test_mcry_2():
    state = quantize_state([1, 3, 1, 3, 1, 3, 1, 3])
    gate = MCRY(
        theta=2 * np.arctan(1 / 3),
        control_qubits=[QBit(1), QBit(2)],
        phases=[0, 0],
        target_qubit=QBit(0),
    )
    new_state = gate.apply(state)
    assert 0b000 not in new_state.index_set
    assert 0b001 in new_state.index_set
    assert 0b010 in new_state.index_set
    assert 0b011 in new_state.index_set
    assert 0b100 in new_state.index_set
    assert 0b101 in new_state.index_set
    assert 0b110 in new_state.index_set
    assert 0b111 in new_state.index_set
    assert np.isclose(new_state.index_to_weight[0b001], 0.5)


def test_mcry_3():
    state = quantize_state([-1, 3, 1, 3, 1, 3, 1, 3])
    gate = MCRY(
        theta=2 * np.arctan(-1 / 3),
        control_qubits=[QBit(1), QBit(2)],
        phases=[0, 0],
        target_qubit=QBit(0),
    )
    new_state = gate.apply(state)
    assert 0b000 not in new_state.index_set
    assert 0b001 in new_state.index_set
    assert 0b010 in new_state.index_set
    assert 0b011 in new_state.index_set
    assert 0b100 in new_state.index_set
    assert 0b101 in new_state.index_set
    assert 0b110 in new_state.index_set
    assert 0b111 in new_state.index_set
    assert np.isclose(new_state.index_to_weight[0b001], 0.5)


def test_mcry_4():
    state = quantize_state([1, -3, 1, 3, 1, 3, 1, 3])
    gate = MCRY(
        theta=2 * np.arctan(-1 / 3),
        control_qubits=[QBit(1), QBit(2)],
        phases=[0, 0],
        target_qubit=QBit(0),
    )
    new_state = gate.apply(state)
    assert 0b000 not in new_state.index_set
    assert 0b001 in new_state.index_set
    assert 0b010 in new_state.index_set
    assert 0b011 in new_state.index_set
    assert 0b100 in new_state.index_set
    assert 0b101 in new_state.index_set
    assert 0b110 in new_state.index_set
    assert 0b111 in new_state.index_set
    assert np.isclose(new_state.index_to_weight[0b001], -0.5)
