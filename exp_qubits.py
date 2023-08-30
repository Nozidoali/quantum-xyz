#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-18 20:05:51
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-18 21:09:09
"""

import datetime
import random
from re import sub
import subprocess
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from qiskit import Aer, transpile
from itertools import combinations
import seaborn as sns
from tomlkit import date

from xyz import QState, synthesize, stopwatch, quantize_state


def rand_state(num_qubit: int, sparsity: int, random_coefficients: bool = False) -> QState:
    """Generate a random state .

    :param num_qubit: [description]
    :type num_qubit: int
    :return: [description]
    :rtype: QState
    """

    if random_coefficients:
        state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
            random.random() for i in range(sparsity)
        ]
    else:
        state_array = [0 for i in range((2**num_qubit) - sparsity)] + [
            1 for i in range(sparsity)
        ]
    np.random.shuffle(state_array)

    return state_array

def place_ones(size, count):
    """Place one or more lists into one .

    :param size: [description]
    :type size: [type]
    :param count: [description]
    :type count: [type]
    :yield: [description]
    :rtype: [type]
    """
    for positions in combinations(range(size), count):
        p = [0] * size
        for i in positions:
            p[i] = 1
        yield p

def all_states(num_qubit: int, sparsity: int) -> QState:
    """Return a QState with all states of the given number of qubit .

    :param num_qubit: [description]
    :type num_qubit: int
    :param sparsity: [description]
    :type sparsity: int
    :return: [description]
    :rtype: QState
    """
    for perm in place_ones(2**num_qubit, sparsity):
        yield perm[:]


def test_synthesis():
    """Test that the synthesis is used ."""

    # state = rand_state(4, 5)
    
    datas = []
    
    for num_qubits in range(2, 8):
        sparsity = num_qubits
        
        valid_states: int = 0
        num_tries = 1000
        num_valid_states = 10
        for i in range(num_tries):
            state = rand_state(num_qubits, sparsity)
            
            qstate = quantize_state(state)
            if len(qstate.get_supports()) != num_qubits:
                continue
            
            valid_states += 1
            if valid_states > num_valid_states:
                break
            
        # for state in all_states(num_qubits, sparsity):
            
            baseline = None
            
            # get the bit string
            state_str = "".join(["1" if x > 0 else "0" for x in state])
            with open("tmp.txt", "w") as f:
                f.write(state_str)
            # baseline
            subprocess.run("qsp_using_sota tmp.txt > tmp.rpt", shell=True , stdout=subprocess.DEVNULL)
                        
            # get the number of cnot
            with open("tmp.rpt", "r") as f:
                for line in f:
                    if "cnots" in line:
                        baseline = int(sub("[^0-9]", "", line))
                        break

            if baseline is None:
                continue
            
            with stopwatch("synthesis") as timer:
                try:
                    circuit = synthesize(state, optimality_level=1)
                except ValueError:
                    print(f"cannot synthesize state {state}")
                    continue
                circ = circuit.to_qiskit()
                simulator = Aer.get_backend("aer_simulator")
                circ = transpile(circ, simulator)

            # Run and get counts
            result = simulator.run(circ).result()
            counts = result.get_counts(circ)

            # print(counts)
            ours = circ.count_ops()["cx"] if "cx" in circ.count_ops() else 0
            print(f"num_qubit = {num_qubits} sparsity = {sparsity} state = {state} baseline = {baseline} ours = {ours}, time = {timer.time()}")
            
            data = {"num_qubit": num_qubits, "sparsity": sparsity, "baseline": baseline, "ours": ours, "time": timer.time()}
            datas.append(data)
    
    df = pd.DataFrame(datas)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    df.to_csv(f"synthesis_{timestamp}.csv")

def analyze_runtime(filename: str):

    plt.rcParams["figure.figsize"] = (10, 10)

    global_font_size = 24

    # move up the bottom of the plot
    plt.rcParams["figure.subplot.bottom"] = 0.1

    # adjust the margin
    plt.rcParams["figure.subplot.left"] = 0.2
    plt.rcParams["figure.subplot.right"] = 0.99
    
    # axis font size
    plt.rcParams["axes.labelsize"] = global_font_size
    plt.rcParams["axes.titlesize"] = global_font_size
    plt.rcParams["xtick.labelsize"] = global_font_size
    plt.rcParams["ytick.labelsize"] = global_font_size
    
    # legend font size
    plt.rcParams["legend.fontsize"] = global_font_size
    
    # legend title font size
    plt.rcParams["legend.title_fontsize"] = global_font_size
    
    # read the data
    # time stamp
    df = pd.read_csv(filename)
    
    # aggregate based on num_qubit
    df_agg = df.groupby(["num_qubit"]).agg({"time": "mean"})
    # calculate the standard deviation
    df_agg["num_cnot_std"] = df.groupby(["num_qubit"]).agg({"time": "std"})["time"]
    
    # plot the bar plot, with the error bar
    df_agg.plot.bar(y=["time"], rot=0)
    
    # data labels of the mean
    data_label_font_size = global_font_size
    precision = 2
    for index, row in df_agg.iterrows():
        plt.text(index - 3 + 0.15, row["time"] + 0.1, f"{row['time']:.{precision}f}", color="black", fontsize=data_label_font_size)
    
    # error bar
    plt.errorbar(df_agg.index - 3, df_agg["time"], yerr=df_agg["num_cnot_std"], fmt='none', ecolor='black', capsize=5)

    # y log scale
    # plt.yscale("log")

    # x axis title
    plt.xlabel("Number of qubits")
    
    # y axis title
    plt.ylabel("Runtime (sec)")
    
    plt.show()

def analyze_data(filename: str):
    
    # adjust figure size
    plt.rcParams["figure.figsize"] = (8, 6)
    
    global_font_size = 24
    
    # axis font size
    plt.rcParams["axes.labelsize"] = global_font_size
    plt.rcParams["axes.titlesize"] = global_font_size
    plt.rcParams["xtick.labelsize"] = global_font_size
    plt.rcParams["ytick.labelsize"] = global_font_size
    
    # legend font size
    plt.rcParams["legend.fontsize"] = global_font_size
    
    # move up the bottom of the plot
    plt.rcParams["figure.subplot.bottom"] = 0.2

    # adjust the margin
    plt.rcParams["figure.subplot.left"] = 0.10
    plt.rcParams["figure.subplot.right"] = 0.99
    
    df = pd.read_csv(filename)
    
    # aggregate based on num_qubit
    df_agg = df.groupby(["num_qubit"]).agg({"baseline": "mean", "ours": "mean", "time": "mean"})
    # calculate the standard deviation
    df_agg["num_cnot_baseline_std"] = df.groupby(["num_qubit"]).agg({"baseline": "std"})["baseline"]
    df_agg["num_cnot_std"] = df.groupby(["num_qubit"]).agg({"ours": "std"})["ours"]
    
    # plot the bar plot, with the error bar
    df_agg.plot.bar(y=["baseline", "ours"], rot=0)
    
    # data points
    if False:
        plt.scatter(df["num_qubit"] - 2 - 0.13, df["baseline"], marker="x", color="black", alpha=0.2)
        plt.scatter(df["num_qubit"] - 2 + 0.13, df["ours"], marker="x", color="black", alpha=0.2)
    
    # data labels of the mean 
    data_label_font_size = global_font_size
    precision = 0
    for index, row in df_agg.iterrows():
        plt.text(index - 3 - 0.11, row["baseline"] + 10 + 0.1, f"{row['baseline']:.{precision}f}", color="black", fontsize=data_label_font_size)
        plt.text(index - 3 + 0.15, row["ours"] + 0.1, f"{row['ours']:.{precision}f}", color="black", fontsize=data_label_font_size)
    
    # with an offset
    plt.errorbar(df_agg.index - 3 - 0.13, df_agg["baseline"], yerr=df_agg["num_cnot_baseline_std"], fmt='none', ecolor='black', capsize=5)
    plt.errorbar(df_agg.index - 3 + 0.13, df_agg["ours"], yerr=df_agg["num_cnot_std"], fmt='none', ecolor='black', capsize=5)
    
    # y axis title
    plt.ylabel("Number of CNOTs")
    
    # x axis title
    plt.xlabel("Number of qubits")
    
    plt.show()

if __name__ == "__main__":
    test_synthesis()
    # analyze_data("synthesis_7_20230829-195112.csv")
    # analyze_runtime("synthesis_7_20230829-195112.csv")