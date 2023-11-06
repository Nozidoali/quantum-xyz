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
    packages=find_packages(include=["xyz", "xyz.*"]),
    install_requires=[
        """
            llist==0.7.1
            matplotlib==3.7.1
            numpy==1.23.5
            qiskit==0.43.1
            qiskit_ibmq_provider==0.20.2
            qiskit_terra==0.24.1
            scipy==1.10.1
            setuptools==67.8.0
        """
    ],
)
