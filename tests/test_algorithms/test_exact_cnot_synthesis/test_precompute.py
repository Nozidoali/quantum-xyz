#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-05-11 18:36:34
Last Modified by: Hanyu Wang
Last Modified time: 2024-05-11 18:37:29
"""

import numpy as np
import xyz


def test_precompute_1():
    db = xyz.QSPDatabase()
    db.load_database(3)
