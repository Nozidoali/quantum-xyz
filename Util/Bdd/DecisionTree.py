#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-17 08:16:40
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-17 08:16:43
"""

class DecisionTreeNode:

    def __init__(self) -> None:
        
        self.left_node = None
        self.right_node = None

        self.pivot_index = None
        self.pivot_value = None

class DecisionTree:

    def __init__(self) -> None:
        self.root = None
        self.nodes = []
        

        self.const1 = DecisionTreeNode()
        self.const0 = DecisionTreeNode()

    def __str__(self) -> str:
        pass
