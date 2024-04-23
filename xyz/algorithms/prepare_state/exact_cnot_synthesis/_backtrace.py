#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-04-23 08:54:47
Last Modified by: Hanyu Wang
Last Modified time: 2024-04-23 08:57:04
"""

from xyz.circuit import QState


def backtrace(state: QState, record: dict):
    gates = []
    backtraced_states: set = set()
    curr_hash = hash(state)
    while curr_hash in record:
        if curr_hash in backtraced_states:
            raise ValueError("Loop found")
        backtraced_states.add(curr_hash)
        prev_hash, _gates = record[curr_hash]
        gates += _gates
        curr_hash = prev_hash

    return gates
