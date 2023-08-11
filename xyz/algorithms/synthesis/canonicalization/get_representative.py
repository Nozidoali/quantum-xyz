#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-11 22:26:09
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-11 23:55:28
"""

from typing import List, Tuple

from xyz.circuit import QOperator, QState, QTransition, XOperator, PureState
from xyz.utils import call_with_global_timer


class CanonicalizationParams:
    """Classicalizes the class for CanonicalizationParams ."""

    run_once: bool = False
    use_swap: bool = True


@call_with_global_timer
def get_representative(
    state: QState, num_qubits: int, enable_swap: bool = True, verbose: bool = False
) -> Tuple[QState, List[QOperator]]:
    """
    Given a quantum state and the number of qubits, find a representative state and a list of quantum operators that transform the initial state to the representative state.

    The transition we returns turn the canonical state to the state that user gave.

    @param state - the initial quantum state
    @param num_qubits - the number of qubits
    @return A tuple containing the representative state and a list of quantum operators, in the class of the QTransition class.
    """

    # if the state is empty, return the empty state.
    if num_qubits == 0:
        return state, None

    curr_state = state.copy()
    prev_state = None
    transitions = QTransition(num_qubits)

    counter: int = 0

    while True:
        counter += 1
        if counter > 100:
            print(
                f"counter > 100, prev_state = \n{prev_state}\n, curr_state = \n{curr_state}\n"
            )
            exit(0)

        if verbose:
            print(f"prev_state = \n{prev_state}\n, curr_state = \n{curr_state}\n")

        prev_state = curr_state.copy()

        if CanonicalizationParams.use_swap and enable_swap:
            column_values_dict = {pivot_qubit: 0 for pivot_qubit in range(num_qubits)}

            sorted_state_array = curr_state.get_sorted_state_array(
                key=lambda x: (x.count_ones(), x), reverse=True
            )
            for i, pure_state in enumerate(sorted_state_array):
                if verbose:
                    print(f"i = {i}, pure_state = {pure_state}")
                for pivot_qubit in range(num_qubits):
                    column_values_dict[pivot_qubit] += (
                        (int(pure_state) >> pivot_qubit) & 1
                    ) << i

            column_values = []
            for pivot_qubit in range(num_qubits):
                if verbose:
                    print(
                        f"pivot_qubit = {pivot_qubit}, column_values_dict[pivot_qubit] = {column_values_dict[pivot_qubit]:b}"
                    )
                column_values.append((column_values_dict[pivot_qubit], pivot_qubit))

            column_values.sort(reverse=True)

            if verbose:
                print(f"column_values = {column_values}")

            new_state = QState([], num_qubits)
            for pure_state in curr_state:
                new_idx = 0

                i = 0
                for num_ones, pivot_qubit in column_values:
                    new_idx |= ((int(pure_state) >> pivot_qubit) & 1) << i
                    i += 1

                if verbose:
                    print(f"pure_state = {pure_state}, new_idx = {new_idx}")
                new_state.add_pure_state(PureState(new_idx))

            curr_state = new_state

        # we need to exhaustively try all the possible flips
        original_state = curr_state.copy()
        best_state = curr_state.copy()
        best_x_index = 0  # 0 means nothing is flipped.

        for x_index in range(1 << num_qubits):
            curr_state = original_state.copy()
            for pivot_qubit in range(num_qubits):
                qubit_is_flipped = ((x_index >> pivot_qubit) & 1) == 1

                if qubit_is_flipped:
                    op = XOperator(pivot_qubit)
                    curr_state = op(curr_state)

            # This is problematic.
            # Because basically we might be able to find a better state if we flip multiple qubits.
            # However, this method now only allow us to find the solution that can be found by flipping one qubit.
            if curr_state < best_state:
                # transitions.add_transition_to_front(x_state, op, curr_state)
                best_state = curr_state.copy()
                best_x_index = x_index

        curr_state = original_state.copy()
        for pivot_qubit in range(num_qubits):
            qubit_is_flipped = ((best_x_index >> pivot_qubit) & 1) == 1

            if qubit_is_flipped:
                op = XOperator(pivot_qubit)
                new_state = op(curr_state)
                transitions.add_transition_to_front(new_state, op, curr_state)
                curr_state = new_state

        if (
            CanonicalizationParams.run_once
            or not enable_swap
            or not CanonicalizationParams.use_swap
            or curr_state == prev_state
        ):
            break

    return curr_state, transitions
