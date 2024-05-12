#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-11 15:20:01
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-11 15:37:42
"""

import numpy as np
import xyz


def test_state_transitions_1():
    state_vector = "0.5*|00>+0.5*|01>+0.5*|10>+0.5*|11>"
    state = xyz.quantize_state(state_vector)
    circuit = xyz.QCircuit(2)
    transitions = xyz.get_state_transitions(circuit, state)

    assert len(transitions) == 1, "len(transitions) = %s" % len(transitions)
    new_state, gates = transitions[0]
    assert new_state == xyz.QState.ground_state(2), "new_state = %s" % new_state
    for gate in gates:
        new_state = gate.apply(new_state)

    assert np.linalg.norm(state.to_vector() - new_state.to_vector()) < 1e-6, (
        "state = %s" % state
    )


def test_state_transitions_2():
    state_vector = "0.5*|00>+0.5*|11>"
    state = xyz.quantize_state(state_vector)
    circuit = xyz.QCircuit(2)
    transitions = xyz.get_state_transitions(circuit, state)

    assert len(transitions) == 1, "len(transitions) = %s" % len(transitions)
    new_state, gates = transitions[0]
    assert new_state == xyz.QState.ground_state(2), "new_state = %s" % new_state
    for gate in gates:
        new_state = gate.apply(new_state)

    assert (
        sum([gate.get_cnot_cost() for gate in gates]) == 1
    ), "sum([gate.get_cnot_cost() for gate in gates]) = %s" % sum(
        [gate.get_cnot_cost() for gate in gates]
    )

    assert np.linalg.norm(state.to_vector() - new_state.to_vector()) < 1e-6, (
        "state = %s" % state
    )


def test_state_transitions_3():
    state_vector = "0.5*|00>+0.5*|01>+0.5*|11>"
    state = xyz.quantize_state(state_vector)
    circuit = xyz.QCircuit(2)
    transitions = xyz.get_state_transitions(circuit, state)

    # assert len(transitions) == 1, "len(transitions) = %s" % len(transitions)
    cry_count: int = 0
    cx_count: int = 0
    for new_state, gates in transitions:
        for gate in gates:
            if isinstance(gate, xyz.CRY):
                cry_count += 1
            elif isinstance(gate, xyz.CX):
                cx_count += 1

    assert cry_count == 4, "cry_count = %s" % cry_count
    # using heuristic
    assert cx_count == 0, "cx_count = %s" % cx_count
