#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-09-12 02:08:25
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-12 02:43:21
"""

# pylint: skip-file

import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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
    plt.rcParams["figure.subplot.bottom"] = 0.15
    plt.rcParams["figure.subplot.top"] = 0.99

    # adjust the margin
    plt.rcParams["figure.subplot.left"] = 0.08
    plt.rcParams["figure.subplot.right"] = 0.92

    df = pd.read_csv(filename)

    # we only keep the num_qubit every 3
    df = df[df["num_qubit"] % 3 == 2]

    # aggregate based on num_qubit
    df_agg = df.groupby(["num_qubit"]).agg(
        {"baseline": "mean", "ours": "mean", "time": "mean"}
    )
    # calculate the standard deviation
    df_agg["num_cnot_baseline_std"] = df.groupby(["num_qubit"]).agg(
        {"baseline": "std"}
    )["baseline"]
    df_agg["num_cnot_std"] = df.groupby(["num_qubit"]).agg({"ours": "std"})["ours"]

    # plot the bar plot, with the error bar
    df_agg.plot.bar(y=["baseline", "ours"], rot=0)

    # data points
    if False:
        plt.scatter(
            df["num_qubit"] - 2 - 0.13,
            df["baseline"],
            marker="x",
            color="black",
            alpha=0.2,
        )
        plt.scatter(
            df["num_qubit"] - 2 + 0.13, df["ours"], marker="x", color="black", alpha=0.2
        )

    min_qubit = df_agg.index.min()
    max_qubit = df_agg.index.max()

    num_bars = len(df_agg.index) - 1

    # data labels of the mean
    data_label_font_size = global_font_size - 4
    precision = 0
    for index, row in df_agg.iterrows():
        plt.text(
            num_bars * (index - min_qubit) / (max_qubit - min_qubit) - 0.6,
            row["baseline"],
            f"{row['baseline']:.{precision}f}",
            color="black",
            fontsize=data_label_font_size,
        )
        plt.text(
            num_bars * (index - min_qubit) / (max_qubit - min_qubit),
            row["ours"],
            f"{row['ours']:.{precision}f}",
            color="black",
            fontsize=data_label_font_size,
        )

    # y axis title
    plt.ylabel("Number of CNOTs")

    plt.yticks([])

    # y log scale
    # plt.yscale("log")

    # x axis title
    plt.xlabel("Number of qubits")

    plt.show()


def analyze_runtime(filename: str):
    plt.rcParams["figure.figsize"] = (10, 10)

    global_font_size = 32

    # move up the bottom of the plot
    plt.rcParams["figure.subplot.bottom"] = 0.1

    # adjust the margin
    plt.rcParams["figure.subplot.left"] = 0.10
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

    df = df[df["num_qubit"] >= 8]

    # change the name of sparsity
    df["sparsity"] = df["sparsity"].map(
        {1: r"$m\sim n$", 2: r"$m\sim n^2$", 3: r"$m\sim n^3$"}
    )

    # scatter plot
    sns.scatterplot(
        data=df,
        x="num_qubit",
        y="time",
        hue="sparsity",
        palette=sns.color_palette("hls", 3),
        marker="s",
        s=200,
    )

    # line plot for each sparsity
    sns.lineplot(
        data=df,
        x="num_qubit",
        y="time",
        hue="sparsity",
        palette=sns.color_palette("hls", 3),
        linewidth=3,
        legend=False,
    )

    # y log scale
    # plt.yscale("log")

    # x axis title
    plt.xlabel("Number of qubits")

    # y axis title
    plt.ylabel("Runtime (sec)")

    plt.show()


BEST_CNOT_QASM_FOLDER = "best_cnot_results"
BEST_CNOT_RESULT_FILE = "best_cnot_results.json"

if __name__ == "__main__":
    best_cnot_results = json.load(
        open(os.path.join(BEST_CNOT_QASM_FOLDER, BEST_CNOT_RESULT_FILE), "r")
    )

    datas = []
    for filename, result in best_cnot_results.items():
        num_qubits, sparsity = filename.replace(".json", "").split("_")[1:]

        num_qubits = int(num_qubits)
        sparsity = int(sparsity)

        data = {
            "num_qubit": num_qubits,
            "sparsity": sparsity,
            "time": result["cpu_time"],
            "ours": result["num_cnots"],
            "baseline": result["num_cnots_sparse_uniform"],
        }

        datas.append(data)

    df = pd.DataFrame(datas)

    df.to_csv("data.csv", index=False)

    # analyze_data("data.csv")
    analyze_runtime("data.csv")
