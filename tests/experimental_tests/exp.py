#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-07 23:30:41
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-12 02:33:15
"""

# pylint: skip-file

from tests.experimental_tests.helper import *

if __name__ == "__main__":
    # remove all the previous results
    # if os.path.exists(BEST_CNOT_RESULT_FILE):
    #     os.remove(BEST_CNOT_RESULT_FILE)
    # if os.path.exists(BEST_TIME_RESULT_FILE):
    #     os.remove(BEST_TIME_RESULT_FILE)

    datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # run all experiments in the examples directory
    for filename in os.listdir(EXAMPLE_FOLDER):
        if not filename.endswith(".json"):
            continue

        best_cnot_results = json.load(open(BEST_CNOT_RESULT_FILE, "r"))
        if get_result(best_cnot_results, filename) is not None:
            continue

        # parse the num_qubit and sparsity from the filename
        filename_base = filename.replace(".json", "")

        num_qubit = int(filename_base.split("_")[1])
        sparsity = int(filename_base.split("_")[2])
        if sparsity > 3:
            continue

        if num_qubit >= 21:
            continue

        new_results = run_experiment(filename, map_gates=False)
        update_results(new_results)
