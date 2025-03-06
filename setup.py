#!/usr/bin/env python
# -*- encoding=utf8 -*-
"""
Author: Hanyu Wang
Created time: 2023-11-06 12:22:56
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-06 12:41:58
"""

from setuptools import setup, find_packages

setup(
    name="quantum-xyz",
    version="0.1.0",
    author="Hanyu Wang",
    description="A quantum circuit synthesis library",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=["xyz", "xyz.*"]),
)
