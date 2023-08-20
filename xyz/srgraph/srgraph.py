#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 16:33:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:21:23
"""

from queue import PriorityQueue
import pygraphviz as pgv
import threading

from .operators import QOperator, QState, QuantizedRotationType, MCRYOperator


class SRGraph:
    """Class method to call the transition class ."""

    def __init__(self, num_qubits: int) -> None:
        self.num_qubits = num_qubits

        self.visited_states = set()
        self.state_queue = PriorityQueue()
        self.enquened_states = {}
        self.record = {}
        
        self.threading_lock = threading.Lock()
        self.exploration_threads = []

    def visit(self, state: QState) -> None:
        """Visit the current state and return the result .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        representive: QState = state.representative()
        self.visited_states.add(representive)

    def add_state(self, state: QState, cost: int) -> bool:
        """Add a state to the machine .

        :param state: [description]
        :type state: QState
        :param cost: [description]
        :type cost: int
        :return: [description]
        :rtype: bool
        """

        representive: QState = state.representative()

        if representive in self.visited_states:
            return False

        if (
            representive in self.enquened_states
            and self.enquened_states[representive] <= cost
        ):
            return False

        self.state_queue.put((cost, state))
        self.enquened_states[representive] = cost
        return True

    def init_search(self) -> None:
        """Initialize search state ."""
        self.visited_states.clear()
        self.state_queue = PriorityQueue()
        # self.enquened_states.clear()
        # self.record.clear()

    def add_edge(
        self, state_before: QState, quantum_operator: QOperator, state_after: QState
    ) -> None:
        """Record a operation between state_after and state_after_after_after_after .

        :param state_before: [description]
        :type state_before: QState
        :param quantum_operator: [description]
        :type quantum_operator: QOperator
        :param state_after: [description]
        :type state_after: QState
        """
        repr_before = state_before.representative()
        repr_after = state_after.representative()
        assert repr_before in self.visited_states
        assert repr_after not in self.visited_states
        self.record[state_after] = state_before, quantum_operator

    def get_prev_state(self, state: QState) -> QState:
        """Get the previous state of a state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: QState
        """
        try:
            return self.record[state][0]
        except KeyError:
            return None

    def search_done(self) -> bool:
        """Return True if all search is done .

        :return: [description]
        :rtype: bool
        """
        return self.state_queue.empty()

    def backtrace_state(self, state: QState, max_depth: int = 100):
        """Return a generator that yields the operations from the given state .

        :param state: [description]
        :type state: QState
        :yield: [description]
        :rtype: [type]
        """
        curr_state = state
        curr_depth: int = 0
        collected_states = []
        while curr_state in self.record:

            if curr_state in collected_states:
                loop_str = "\n -> ".join([str(x) for x in collected_states] + [str(curr_state)])
                raise RuntimeError(f"Backtrace loop detected state = {loop_str}")
            collected_states.append(curr_state)
            
            # to avoid infinite loop
            if curr_depth > max_depth:
                raise RuntimeError(f"Backtrace depth exceeded state = {curr_state}")
            curr_depth += 1

            prev_state, quantum_operator = self.record[curr_state]
            yield prev_state, quantum_operator, curr_state
            curr_state = prev_state

    def is_visited(self, state: QState):
        """Returns whether the given state is visited .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: [type]
        """
        return state.representative() in self.visited_states

    @staticmethod
    def get_lower_bound(state: QState) -> int:
        """Returns the lower bound of the state .

        :param state: [description]
        :type state: QState
        :return: [description]
        :rtype: int
        """
        
        lower_bound: int = 0
        for pattern in state.patterns:
            if pattern != 0:
                lower_bound += 1
        return lower_bound

    def thread_explore(self, curr_state: QState, quantum_operator: QOperator, next_state: QState, cost: int):
        """Explore the next state in a thread .

        :param curr_state: [description]
        :type curr_state: QState
        :param next_state: [description]
        :type next_state: QState
        :param cost: [description]
        :type cost: int
        """
        
        # don't use multi-threading if the state is already visited
        self.thread_explore_target(curr_state, quantum_operator, next_state, cost)
        return
        
        task = threading.Thread(target=self.thread_explore_target, args=(curr_state, quantum_operator, next_state, cost))
        self.exploration_threads.append(task)
        task.start()
        
    def wait_exploration_done(self):
        """Wait for all exploration threads to finish ."""
        for task in self.exploration_threads:
            task.join()
        
        self.exploration_threads.clear()
        
    def thread_explore_target(self, state: QState, quantum_operator: QOperator, next_state: QState, cost: int):
        """Explore the next state in a thread .

        :param curr_state: [description]
        :type curr_state: QState
        :param next_state: [description]
        :type next_state: QState
        :param cost: [description]
        :type cost: int
        """
        next_cost = (
            cost + quantum_operator.get_cost() + self.get_lower_bound(next_state)
        )
        representive: QState = next_state.representative()
        
        # avoid thrusting
        with self.threading_lock:
                    
            if representive in self.visited_states:
                # we should not explore visited states
                return

            if (
                representive in self.enquened_states
                and self.enquened_states[representive] <= next_cost
            ):
                # if the state is already enquened with a lower cost, we should not explore it
                return

            self.state_queue.put((next_cost, next_state))
            self.enquened_states[representive] = next_cost
            
            self.record[next_state] = state, quantum_operator
                

    def explore(self, cost: int, state: QState):
        """Return the neighbors of the state .

        :param state: [description]
        :type state: QState
        """
        
        # we first check the signatures of the state
        

        for target_qubit in range(self.num_qubits):
            pos_cofactor, neg_cofactor = state.cofactors(target_qubit)

            # skip if the target qubit is already 1
            if len(pos_cofactor) == 0 or len(neg_cofactor) == 0:
                continue

            if pos_cofactor == neg_cofactor:
                # apply merge0
                quantum_operator = MCRYOperator(
                    target_qubit, QuantizedRotationType.MERGE0, [], []
                )
                next_state = state.apply_merge0(target_qubit)
                self.thread_explore(state, quantum_operator, next_state, cost)

            for control_qubit in range(self.num_qubits):
                if control_qubit == target_qubit:
                    continue

                if state.patterns[control_qubit] == 0:
                    continue

                for phase in [True, False]:

                    pos_cofactor, neg_cofactor = state.controlled_cofactors(
                        target_qubit, control_qubit, phase
                    )

                    if len(pos_cofactor) > 0 and pos_cofactor == neg_cofactor:
                        
                        # apply merge0
                        quantum_operator = MCRYOperator(
                            target_qubit,
                            QuantizedRotationType.MERGE0,
                            [control_qubit],
                            [phase],
                        )
                        next_state = state.apply_controlled_merge0(control_qubit, phase, target_qubit)
                        self.thread_explore(state, quantum_operator, next_state, cost)
                        
                        # apply merge1
                        quantum_operator = MCRYOperator(
                            target_qubit,
                            QuantizedRotationType.MERGE1,
                            [control_qubit],
                            [phase],
                        )
                        next_state = state.apply_controlled_merge1(control_qubit, phase, target_qubit)
                        self.thread_explore(state, quantum_operator, next_state, cost)

                # CNOT
                for phase in [True]:
                    quantum_operator = MCRYOperator(
                        target_qubit, QuantizedRotationType.SWAP, [control_qubit], [phase]
                    )
                    next_state = state.apply_cx(control_qubit, phase, target_qubit)
                    self.thread_explore(state, quantum_operator, next_state, cost)
                
        self.wait_exploration_done()
        
    def __str__(self) -> str:
        graph: pgv.AGraph = pgv.AGraph(directed=True)

        for prev_state, edge_operator, state in self.backtrace_state(QState.ground_state(self.num_qubits)):
            try:
                state_str = str(state).replace("-", "\n")
                graph.add_node(
                    str(state), label=f"{state_str}"
                )
                graph.add_edge(
                    str(prev_state),
                    str(state),
                    label=str(edge_operator) + f"({edge_operator.get_cost()})",
                )
            except KeyError:
                pass
        return graph.string()
