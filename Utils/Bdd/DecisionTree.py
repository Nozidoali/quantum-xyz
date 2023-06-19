#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-17 08:16:40
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-17 08:16:43
"""

import pygraphviz as pgv

class DecisionTreeNode:

    def __init__(self, const_value: int = None) -> None:

        self.negative_cofactor = None
        self.positive_cofactor = None

        self.pivot_index = None
        self.pivot_value = None
        
        self.is_leaf: bool = const_value != None
        self.const_value: int = const_value

class DecisionTree:

    def __init__(self) -> None:
        self.root = None
        self.nodes = []

        self.const1 = DecisionTreeNode( const_value=1 )
        self.const0 = DecisionTreeNode( const_value=0 )

    def __str__(self) -> str:
        pass

    def export(self, filename: str) -> None:
        
        graph = pgv.AGraph()
        graph.add_node("const0", label="0")
        graph.add_node("const1", label="1")
        
        node_index: int = 0

        def export_helper(graph: pgv.AGraph, node):
            if node.is_leaf:
                return graph.get_node("const" + str(node.const_value))
            
            else:
                 
                nonlocal node_index               
                graph.add_node("node" + str(node_index), label="x" + str(node.pivot_index) + " = " + str(node.pivot_value))
                new_node = graph.get_node("node" + str(node_index))
                node_index += 1
                
                positive_node = export_helper(graph, node.positive_cofactor)
                negative_node = export_helper(graph, node.negative_cofactor)
                
                graph.add_edge(new_node, positive_node, label="1")
                graph.add_edge(new_node, negative_node, label="0")
                
                return new_node
        
        export_helper(graph, self.root)
        graph.write(filename)
            