#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-23 11:07:16
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-23 11:26:32
"""

import numpy as np
import matplotlib.pyplot as plt

from typing import List


def print_cube(states: List[int], filename: str):
    fig = plt.figure(figsize=(4, 4))

    ax = fig.add_subplot(111, projection="3d")

    # Define cube vertices
    vertices = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
        ]
    )

    # Define cube edges
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]

    # Draw hollow vertices

    points_x = []
    points_y = []
    points_z = []

    for state in states:
        assert isinstance(state, int)
        assert state in range(8)
        points_x.append(vertices[state, 0])
        points_y.append(vertices[state, 1])
        points_z.append(vertices[state, 2])

    ax.scatter(
        points_x,
        points_y,
        points_z,
        c="red",
        edgecolors="red",
        s=100,
        alpha=1,
        depthshade=False,
        linewidth=3.0,
    )
    # ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], c='blue', edgecolors='blue', s=400, alpha=1.0, depthshade=False, linewidth=5.0)

    # Draw edges
    for edge in edges:
        start = vertices[edge[0]]
        end = vertices[edge[1]]
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            [start[2], end[2]],
            color="black",
            linewidth=3.0,
        )

    # Set plot limits
    ax.set_xlim([-0.5, 1.5])
    ax.set_ylim([-0.5, 1.5])
    ax.set_zlim([-0.5, 1.5])

    # Hide the X-Y-Z plane
    ax.grid(False)

    # Hide the axes
    ax.axis("off")

    plt.savefig(filename, format="pdf")
