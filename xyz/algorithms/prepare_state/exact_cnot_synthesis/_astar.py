#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 08:21:50
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 09:15:33
"""


class AStarCost:
    """AStarCost class ."""

    def __init__(self, cnot_cost: float, lower_bound: float) -> None:
        self.cnot_cost = cnot_cost
        self.lower_bound = lower_bound

    def __lt__(self, other: "AStarCost"):
        return self.cnot_cost + self.lower_bound < other.cnot_cost + other.lower_bound

    def __ge__(self, other: "AStarCost"):
        return self.cnot_cost + self.lower_bound >= other.cnot_cost + other.lower_bound

    def __str__(self) -> str:
        return f"{self.cnot_cost}(+{self.lower_bound})"
