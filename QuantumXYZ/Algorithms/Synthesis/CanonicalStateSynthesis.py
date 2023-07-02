#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 18:52:42
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 19:46:24
"""

from QuantumXYZ.Circuit import *
from .SearchBasedStateSynthesis import *

from typing import List, Tuple

class CanonicalizationParams:
    run_once: bool = True
    use_swap: bool = True

def get_representative(
    state: QState, num_qubits: int, enable_swap: bool = True, verbose: bool = False
) -> Tuple[QState, List[QOperator]]:
    """
    Given a quantum state and the number of qubits, find a representative state and a list of quantum operators that transform the initial state to the representative state.

    The transition we returns turn the canonical state to the state that user gave.

    @param state - the initial quantum state
    @param num_qubits - the number of qubits
    @return A tuple containing the representative state and a list of quantum operators
    """
    if num_qubits == 0:
        return state, []

    curr_state = state.copy()
    prev_state = None
    transitions = QTransition(num_qubits)

    counter: int = 0

    while True:

        counter += 1
        if counter > 100:
            print(f"counter > 100, prev_state = \n{prev_state}\n, curr_state = \n{curr_state}\n")
            exit(0)

        if verbose:
            print(f"prev_state = \n{prev_state}\n, curr_state = \n{curr_state}\n")

        prev_state = curr_state.copy()

        if CanonicalizationParams.use_swap:
            column_values_dict = {pivot_qubit:0 for pivot_qubit in range(num_qubits)}

            sorted_state_array = curr_state.get_sorted_state_array(
                key=lambda x: (x.count_ones(), x),
                reverse=True)
            for i, pure_state in enumerate(sorted_state_array):
                if verbose:
                    print(f"i = {i}, pure_state = {pure_state}")
                for pivot_qubit in range(num_qubits):
                    column_values_dict[pivot_qubit] += ((int(pure_state) >> pivot_qubit) & 1) << i

            column_values = []
            for pivot_qubit in range(num_qubits):
                if verbose:
                    print(f"pivot_qubit = {pivot_qubit}, column_values_dict[pivot_qubit] = {column_values_dict[pivot_qubit]:b}")
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


        for pivot_qubit in range(num_qubits):
            op = XOperator(pivot_qubit)
            x_state = op(curr_state)

            if x_state < curr_state:
                transitions.add_transition_to_front(x_state, op, curr_state)
                curr_state = x_state

        if CanonicalizationParams.run_once or curr_state == prev_state:
            break

    return curr_state, transitions


class CanonicalStateSynthesis(SearchBasedStateSynthesis):
    def __init__(self, target_state: QStateBase) -> None:
        SearchBasedStateSynthesis.__init__(self, target_state)
        self.use_canonical = True

    def visit(self, state: QState) -> None:
        state_repr, _ = get_representative(state, self.num_qubits)
        self.visited_states.add(state_repr)

    def add_state(self, state: QState, cost: int) -> bool:
        state_repr, _ = get_representative(state, self.num_qubits)

        if state_repr in self.visited_states:
            return False

        if (
            state_repr in self.enquened_states
            and self.enquened_states[state_repr] <= cost
        ):
            return False

        self.state_queue.put((cost, state))
        self.enquened_states[state_repr] = cost
        return True

    def is_visited(self, state: QState):
        state_repr, _ = get_representative(state, self.num_qubits)
        return state_repr in self.visited_states

    def get_lower_bound(self, state: QState) -> int:
        """
        Get the lower bound for a given state in a QState object.
        @param state - the state for which to calculate the lower bound
        @return The lower bound as an integer
        """
        return state.num_supports()

    def get_ops(self, state: QState):
        one_counts = state.count_ones()

        # yields the state of the pivot qubit.
        for pivot_qubit_index in range(self.num_qubits):
            # this qubit is a dont care qubit.
            if one_counts[pivot_qubit_index] == 0 or one_counts[
                pivot_qubit_index
            ] == len(state):
                continue

            # yields the rotation state of the current state.
            for rotation_type in [
                QuantizedRotationType.SWAP,
                QuantizedRotationType.MERGE0,
                QuantizedRotationType.MERGE1,
            ]:
                # first we try the case where no control qubit is used
                op = MCRYOperator(
                    target_qubit_index=pivot_qubit_index,
                    rotation_type=rotation_type,
                    control_qubit_indices=[],
                    control_qubit_phases=[],
                )

                yield op

                # Yields the state of the current state of the MCRY operator.
                for control_qubit_index in range(self.num_qubits):
                    # If control_qubit_index is pivot_qubit_index control_qubit_index pivot_qubit_index.
                    if control_qubit_index == pivot_qubit_index:
                        continue

                    # Yields the state of the current state.
                    for control_qubit_phase in [False, True]:
                        op = MCRYOperator(
                            target_qubit_index=pivot_qubit_index,
                            rotation_type=rotation_type,
                            control_qubit_indices=[control_qubit_index],
                            control_qubit_phases=[control_qubit_phase],
                        )

                        yield op
