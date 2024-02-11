#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-15 14:42:39
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-15 14:54:51
"""

import os
from xyz import load_state
from xyz import prepare_state

REGRESSION_TEST_DIR = os.path.join(os.path.dirname(__file__), "regression_testcases")


def save_buggy_state(state):
    """Save the buggy state to a file .

    :param state: [description]
    :type state: [type]
    """

    # we first get the buggy states
    files = os.listdir(REGRESSION_TEST_DIR)

    num_cases = len(files)

    # we then save the buggy state
    state.to_file(os.path.join(REGRESSION_TEST_DIR, f"{num_cases}.json"))


def run():
    """Run the regression test .

    :param state: [description]
    :type state: [type]
    """

    # we first get the buggy states
    files = os.listdir(REGRESSION_TEST_DIR)

    num_cases = len(files)

    # we then check if the current state is a buggy state
    for i in range(num_cases):
        file = os.path.join(REGRESSION_TEST_DIR, f"{i}.json")

        state = load_state(file)
        circuit = prepare_state(state)
        print(circuit.to_qiskit())


if __name__ == "__main__":
    run()
