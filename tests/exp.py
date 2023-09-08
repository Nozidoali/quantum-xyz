#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

import os
import json
import datetime

from xyz import QState, cnot_synthesis, stopwatch, load_state, QGateType

EXAMPLE_FOLDER = os.path.join(os.path.dirname(__file__), "examples")
BEST_CNOT_RESULT_FILE = os.path.join(os.path.dirname(__file__), "best_cnot_results", "best_cnot_results.json")
BEST_CNOT_QASM_FOLDER = os.path.join(os.path.dirname(__file__), "best_cnot_results")
BEST_TIME_RESULT_FILE = os.path.join(os.path.dirname(__file__), "best_time_results", "best_time_results.json")
BEST_TIME_QASM_FOLDER = os.path.join(os.path.dirname(__file__), "best_time_results")

def get_result(results: dict, filename: str):
    """Get the results of the experiment .

    :param results: [description]
    :type results: dict
    :param filename: [description]
    :type filename: str
    :return: [description]
    :rtype: [type]
    """
    if filename not in results:
        return None

    return results[filename]


def run_experiment(filename: str, optimality_level: int = 3, map_gates: bool = False, run_all: bool = True):
    """Run all the experiments in the current directory .

    :param run_all: [description], defaults to True
    :type run_all: bool, optional
    """
    
    new_results = {}
    
    state: QState = load_state(os.path.join(EXAMPLE_FOLDER, filename))
    
    print(f"Running {filename}... state density = {len(state.index_to_weight)}, num_qubits = {state.num_qubits},")

    # run the experiment
    with stopwatch("synthesis") as timer:
        circuit = cnot_synthesis(state, optimality_level=optimality_level, map_gates=map_gates, verbose_level=0)

        # get the CNOT gate count
        
        if map_gates:
            num_cnots: int = circuit.num_gates(QGateType.CX)
        else:
            num_cnots: int = circuit.get_cnot_cost()
        
        circ = circuit.to_qiskit()
        
        #TODO: verify the circuit is correct
        
        # generate a qasm string    
        qasm_str = circ.qasm()
        
    if map_gates:
        
        # double check if the circuit is mapped correctly
        num_cnots_qiskit: int = 0
        for gate, gate_count in circ.count_ops().items():
            if gate == "cx":
                num_cnots_qiskit += gate_count
            elif gate == "cx_oFalse":
                num_cnots_qiskit += gate_count
            elif gate not in ["measure", "ry", "x"]:
                print(f"Illegal gate {gate} in {filename}")
                exit(1)
                pass

        #TODO: verify the gate count is correct
        assert num_cnots == num_cnots_qiskit, f"num_cnots = {num_cnots}, num_cnots_qiskit = {num_cnots_qiskit}"

    cpu_time = timer.time()
    
    # generate a timestamp
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # record the results
    new_results[filename] = {
        "optimality_level": optimality_level,
        "cpu_time": cpu_time,
        "qasm_str": qasm_str,
        "date_time": date_time,
        "num_cnots": num_cnots,
    }
        
    # save the results
    return new_results

def separate_qasm_from_results(new_results: dict):
    """Separate qasm_stats and qasm_stats into a dictionary with qasm_qasm_qasm_stats and qasm_stats .

    :param new_results: [description]
    :type new_results: dict
    :return: [description]
    :rtype: [type]
    """
    
    # we separate the QASM from the results
    new_results_stats = {}
    qasms = {}
    for filename, result in new_results.items():
        new_results_stats[filename] = {}
        for key, value in result.items():
            if key == "qasm_str":
                qasms[filename] = value
            else:
                new_results_stats[filename][key] = value

    return new_results_stats, qasms

def compare_and_update_results(best_result_filename: str, new_results: dict, best_qasm_dir, qasms: dict, key: str):
    """Compare and update the results of the latest run.

    :param best_result_filename: [description]
    :type best_result_filename: str
    :param new_results: [description]
    :type new_results: dict
    :param key: [description]
    :type key: str
    """
    
    # load the best results
    with open(best_result_filename, "r") as f:
        best_results = json.load(f)
        
    # update the best results
    for filename, result in new_results.items():
        best_result = get_result(best_results, filename)
        if best_result is None or result[key] < best_result[key]:
            best_results[filename] = result
            
            # replace the qasm file
            qasm_filename = filename.replace(".json", ".qasm")
            with open(os.path.join(best_qasm_dir, qasm_filename), "w") as f:
                f.write(qasms[filename])
    
    # sort the best results
    best_results = dict(sorted(best_results.items(), key=lambda x: x[1][key]))

    # save the best results
    with open(best_result_filename, "w") as f:
        json.dump(best_results, f, indent=2)

def update_results(new_results: dict):
    """Update the results of the latest run .

    :param new_results: [description]
    :type new_results: dict
    """
    
    new_results_stats, qasms = separate_qasm_from_results(new_results)
    
    
    # update the best results
    
    for best_result_filename, qasm_dir, key in zip(
        [BEST_CNOT_RESULT_FILE, BEST_TIME_RESULT_FILE], 
        [BEST_CNOT_QASM_FOLDER, BEST_TIME_QASM_FOLDER],
        ["num_cnots", "cpu_time"]
    ):
        if not os.path.exists(best_result_filename):
            with open(best_result_filename, "w") as f:
                json.dump(new_results_stats, f)
            for best_result_filename, qasm_str in qasms.items():
                assert best_result_filename.endswith(".json")
                qasm_filename = best_result_filename.replace(".json", ".qasm")
                with open(os.path.join(qasm_dir, qasm_filename), "w") as f:
                    f.write(qasm_str)
            continue
        

        compare_and_update_results(best_result_filename, new_results_stats, qasm_dir, qasms, key)

    

if __name__ == "__main__":
    
    # run all experiments in the examples directory
    for filename in os.listdir(EXAMPLE_FOLDER):
        
        if not filename.endswith(".json"):
            continue
        
        # parse the num_qubit and sparsity from the filename
        filename_base = filename.replace(".json", "")
        
        num_qubit = int(filename_base.split("_")[1])
        sparsity = int(filename_base.split("_")[2])
        if sparsity > 3:
            continue

        if num_qubit >= 21:
            continue
    
        new_results = run_experiment(filename, map_gates = False)
        update_results(new_results)
