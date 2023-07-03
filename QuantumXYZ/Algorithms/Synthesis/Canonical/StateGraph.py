#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-07-03 10:06:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-07-03 14:20:13
'''

from QuantumXYZ.Circuit import *

class StateGraph:

    def __init__(self) -> None:
        self.nodes = set()
        self.edges = {}
    
    def add_node(self, node: PureState) -> None:
        if node in self.nodes:
            return
        self.nodes.add(node)
        self.edges[node] = set()

    def add_edge(self, node1: PureState, node2: PureState) -> None:
        if node1 not in self.nodes:
            self.add_node(node1)
        if node2 not in self.nodes:
            self.add_node(node2)
        self.edges[node1].add(node2)
        self.edges[node2].add(node1)

    def get_degree(self, node: PureState) -> int:
        return len(self.edges[node])

    def __str__(self) -> str:
        return_str = ""
        for node in self.nodes:
            return_str += str(node) + ": "
            for edge in self.edges[node]:
                return_str += str(edge) + " "
            return_str += "\n"
        return return_str

def state_to_graph(state: QState) -> StateGraph:
    graph = StateGraph()

    sorted_states = state.get_sorted_state_array()

    for i in range(len(sorted_states)):

        # we need to add the node whether it is adjacent to other nodes or not
        graph.add_node(sorted_states[i])

        # we add edges between adjacent nodes
        for j in range(i + 1, len(sorted_states)):
            if sorted_states[i].is_adjacent(sorted_states[j]):
                graph.add_edge(sorted_states[i], sorted_states[j])

    return graph