#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 18:52:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 19:46:24
"""

from xyz.circuit import QState, QuantizedRotationType, MCRYOperator

from .canonicalization import get_representative


def _visit(self, state: QState) -> None:
    """Visit the given state and store it in the state .

    :param state: [description]
    :type state: QState
    """
    state_repr, _ = get_representative(state, self.num_qubits)
    self.visited_states.add(state_repr)


def _add_state(self, state: QState, cost: int) -> bool:
    """Add a state to the queue .

    :param state: [description]
    :type state: QState
    :param cost: [description]
    :type cost: int
    :return: [description]
    :rtype: bool
    """
    state_repr, _ = get_representative(state, self.num_qubits)

    if state_repr in self.visited_states:
        return False

    if state_repr in self.enquened_states and self.enquened_states[state_repr] <= cost:
        return False

    self.state_queue.put((cost, state))
    self.enquened_states[state_repr] = cost
    return True


def _is_visited(self, state: QState):
    """Returns True if the state is visited by the state .

    :param state: [description]
    :type state: QState
    :return: [description]
    :rtype: [type]
    """
    state_repr, _ = get_representative(state, self.num_qubits)
    return state_repr in self.visited_states


def _get_lower_bound(state: QState) -> int:
    """Returns the lower bound of the given state .

    :param state: [description]
    :type state: QState
    :return: [description]
    :rtype: int
    """
    return state.num_supports()


def _get_operators(self, state: QState):
    """Given a state and a state return a list of operator operators .

    :param state: [description]
    :type state: QState
    :yield: [description]
    :rtype: [type]
    """
    one_counts = state.count_ones()

    # yields the state of the pivot qubit.
    for pivot_qubit_index in range(self.num_qubits):
        # this qubit is a dont care qubit.
        if one_counts[pivot_qubit_index] == 0 or one_counts[pivot_qubit_index] == len(
            state
        ):
            continue

        # yields the rotation state of the current state.
        for rotation_type in [
            QuantizedRotationType.SWAP,
            QuantizedRotationType.MERGE0,
            QuantizedRotationType.MERGE1,
        ]:
            # first we try the case where no control qubit is used
            operator = MCRYOperator(
                target_qubit_index=pivot_qubit_index,
                rotation_type=rotation_type,
                control_qubit_indices=[],
                control_qubit_phases=[],
            )

            yield operator

            # Yields the state of the current state of the MCRY operatorerator.
            for control_qubit_index in range(self.num_qubits):
                # If control_qubit_index is pivot_qubit_index control_qubit_index pivot_qubit_index.
                if control_qubit_index == pivot_qubit_index:
                    continue

                # Yields the state of the current state.
                for control_qubit_phase in [False, True]:
                    operator = MCRYOperator(
                        target_qubit_index=pivot_qubit_index,
                        rotation_type=rotation_type,
                        control_qubit_indices=[control_qubit_index],
                        control_qubit_phases=[control_qubit_phase],
                    )

                    yield operator
