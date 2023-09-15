#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-08-31 14:22:40
Last Modified by: Hanyu Wang
Last Modified time: 2023-08-31 16:45:52
"""

# pylint: skip-file

from xyz import read_truth_table, convert_tt_to_sop
from xyz import sop_to_str


def test_tt_to_sop():
    tt = read_truth_table("110-1-00")
    sop = convert_tt_to_sop(tt)
    print(sop_to_str(sop))


if __name__ == "__main__":
    test_tt_to_sop()
