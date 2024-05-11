#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-20 18:47:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:08:10
"""


class QBit:
    """Class method for creating a bit class ."""

    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f"q{self.index}"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, QBit):
            return self.index == __value.index
        return False

    def __hash__(self) -> int:
        return hash(self.index)
