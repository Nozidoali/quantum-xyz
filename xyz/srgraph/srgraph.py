#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-28 16:33:50
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-28 17:21:23
"""

import pygraphviz as pgv


class SRGraph:
    """Class method to call the transition class ."""

    def __init__(self, num_qubits: int) -> None:
        self.num_qubits = num_qubits

    def __str__(self) -> str:
        graph: pgv.AGraph = pgv.AGraph(directed=True)

        for prev_state, edge_operator, state in self.backtrace_state(
            QState.ground_state(self.num_qubits)
        ):
            try:
                state_str = str(state).replace("-", "\n")
                graph.add_node(str(state), label=f"{state_str}")
                graph.add_edge(
                    str(prev_state),
                    str(state),
                    label=str(edge_operator) + f"({edge_operator.get_cost()})",
                )
            except KeyError:
                pass
        return graph.string()
