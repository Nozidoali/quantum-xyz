#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 14:39:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:25:35
"""

from typing import List

import numpy as np


class RotationGate:
    """Classmethod to handle RotationGate ."""

    def __init__(self, theta: float) -> None:
        self.theta = theta

    def is_trivial(self) -> bool:
        """Whether the model is trivial to be trivial .

        :return: [description]
        :rtype: bool
        """
        return np.isclose(self.theta, 0) or np.isclose(self.theta, 2 * np.pi)

    def is_pi(self) -> bool:
        """True if theta is a pi - > pi .

        :return: [description]
        :rtype: bool
        """
        return np.isclose(self.theta, np.pi) or np.isclose(self.theta, -np.pi)

    def get_theta(self) -> float:
        """Get the theta of the rotation gate .

        :return: [description]
        :rtype: float
        """
        return self.theta


class MultiRotationGate:
    """Class method for creating a new rotation gate ."""

    def __init__(self, thetas: List[float]) -> None:
        self.thetas = thetas
