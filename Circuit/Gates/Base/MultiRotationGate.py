#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-22 23:57:27
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-22 23:58:15
"""

import numpy as np
from typing import List

from .QGate import *
from .QBit import *


class MultiRotationGate:
    def __init__(self, thetas: List[float]) -> None:
        self.thetas = thetas
