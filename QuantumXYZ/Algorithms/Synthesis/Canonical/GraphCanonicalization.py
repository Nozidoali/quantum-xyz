#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-07-03 13:48:49
Last Modified by: Hanyu Wang
Last Modified time: 2023-07-03 14:24:04
'''

from QuantumXYZ.Circuit import *
from .StateGraph import *

def canonicalize(state: QState) -> QState:
    
    graph = state_to_graph(state)

    node_degrees = [(graph.get_degree(node), node) for node in graph.nodes]
    node_degrees.sort(key=lambda x: x[0], reverse=True)
    
    node_taken = set()

    # we need to run a dfs to get the canonical state

    for node_degree in node_degrees:
        print(node_degree)

    state_array = []
    for node in graph.nodes:
        assert isinstance(node, PureState)
        state_array.append(node)

    print(graph)
    
    return QState(state_array, state.get_num_qubits(), True)