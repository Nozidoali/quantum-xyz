#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-09-17 15:49:02
Last Modified by: Hanyu Wang
Last Modified time: 2023-09-17 17:33:45
'''

# pylint: skip-file

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyparsing import col
import seaborn as sns

DENSE: bool = False

df = pd.read_csv('runtime_bak.csv')

# we aggregate the data by the number of qubits
# we slice the data, only consider the case where n > 5
df = df[df['num_qubits'] > 5]

df_dense = df[df['cardinality'] == r"$m = 2^{n-1}$"]
df_sparse = df[df['cardinality'] == r"$m = n$"]

df_dense_state_agg = df_dense.groupby(['num_qubits', 'method']).mean()
df_sparse_state_agg = df_sparse.groupby(['num_qubits', 'method']).mean()

df_sparse_uncertainty = df_sparse.groupby(['num_qubits', 'method']).std()
df_dense_uncertainty = df_dense.groupby(['num_qubits', 'method']).std()

# plot the lineplot
sns.set_theme(style="darkgrid")
sns.set(font_scale=1.5)
sns.set_style("ticks")
sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 2.5})

# set the figure size
plt.figure(figsize=(6, 8))

# figure margin
plt.subplots_adjust(left=0.18, right=0.95, top=0.99, bottom=0.09)

font_size = 24

# set y x title
plt.ylabel("Runtime (s)", fontsize=font_size)
plt.xlabel("Number of qubits", fontsize=font_size)

# set the color palette
sns.set_palette("muted")

hue_order = [
    "n-flow",
    "m-flow",
    "ours"
]

# plot the sparse data
ax = sns.lineplot(
    data=df_dense_state_agg if DENSE else df_sparse_state_agg,
    x="num_qubits",
    y="time",
    hue="method",
    hue_order=hue_order,
    # legend=False,
)

# plot the error bar
# if DENSE:
#     ax.errorbar(
#         x=df_dense_state_agg.index.get_level_values('num_qubits'),
#         y=df_dense_state_agg['time'],
#         yerr=df_dense_uncertainty['time'],
#         fmt='none',
#         capsize=5,
#         elinewidth=2,
#         markeredgewidth=2,
#         color='k',
#         label=None
#     )
# else:
#     ax.errorbar(
#         x=df_sparse_state_agg.index.get_level_values('num_qubits'),
#         y=df_sparse_state_agg['time'],
#         yerr=df_sparse_uncertainty['time'],
#         fmt='none',
#         capsize=5,
#         elinewidth=2,
#         markeredgewidth=2,
#         color='k',
#         label=None
#     )

# plot the data points
# make sure we use the same color palette
ax = sns.scatterplot(
    data=df_dense if DENSE else df_sparse,
    x="num_qubits",
    y="time",
    hue="method",
    # hue_norm=hue_order,
    marker="+",
    s=500,
    ax=ax,
    alpha=0.3,
    legend=False,
)

customize_legend_names = {
    "n-flow": r"$n$-flow",
    "m-flow": r"$m$-flow",
    "ours": "ours",
}


if DENSE:
    # plot a red line at y = 3600
    ax.axhline(y=3600, color='r', linestyle='-')

    # add the text "Time limit = 1 hour"
    ax.text(6.5, 3600*1.1, "Time limit = 1 hour", fontsize=font_size, color='r')

# get the handles and labels
handles, labels = ax.get_legend_handles_labels()

# replace the labels
labels = [customize_legend_names[label] for label in labels]

# plot the legend
ax.legend(handles=handles, labels=labels, fontsize=font_size)

# y log scale
ax.set_yscale("log")

# save the figure
if DENSE:
    plt.savefig("runtime_dense_state.pdf", bbox_inches='tight')
else:
    plt.savefig("runtime_sparse_state.pdf", bbox_inches='tight')

plt.show()