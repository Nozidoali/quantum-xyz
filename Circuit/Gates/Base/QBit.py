#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-20 18:47:08
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 15:08:10
"""


class QBit:
    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f"QBit({self.index})"
