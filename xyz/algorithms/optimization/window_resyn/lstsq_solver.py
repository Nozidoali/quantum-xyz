#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2024-03-18 17:00:39
Last Modified by: Hanyu Wang
Last Modified time: 2024-03-18 17:34:06
"""

import numpy as np


class LstSqSolverVar:
    def __init__(self, index: int = None) -> None:
        self.index = index


class LstSqSolver:
    def __init__(self) -> None:
        self._variables = {}
        self._n_vars: int = 0
        self._n_constraints: int = 0
        self._solutions = None
        self._A = []
        self._b = []

    def add_variable(self, name: str) -> LstSqSolverVar:
        new_var = LstSqSolverVar(self._n_vars)
        self._n_vars += 1
        self._variables[name] = new_var
        return new_var

    def get_variable(self, name: str) -> LstSqSolverVar:
        return self._variables[name]

    def get_n_variables(self) -> int:
        return self._n_vars

    def get_n_constraints(self) -> int:
        return self._n_constraints

    def add_constraint(
        self, variables: list, coefficients: list, value: float = 0
    ) -> None:
        assert len(variables) == len(coefficients)
        vector = [0] * self._n_vars
        for i, v in enumerate(variables):
            if isinstance(v, LstSqSolverVar):
                vector[v.index] = coefficients[i]
            elif isinstance(v, int):
                vector[v] = coefficients[i]
            elif isinstance(v, str):
                vector[self._variables[v].index] = coefficients[i]
            else:
                raise ValueError("Invalid variable type")
        self._A.append(vector)
        self._b.append(value)
        self._n_constraints += 1

    def solve(self) -> None:

        sol, residuals, _, _ = np.linalg.lstsq(self._A, self._b, rcond=None)
        if residuals.size > 0 and np.allclose(residuals, 0):
            self._solutions = sol
            if not np.allclose(np.dot(self._A, sol), self._b):
                return False
            return True
        elif residuals.size == 0:
            if not np.allclose(np.dot(self._A, sol), self._b):
                # print("residuals.size == 0")
                # print("sol: ", sol)
                # print(f"difference: {np.dot(self._A, sol) - self._b}")
                return False
            self._solutions = sol
            return True
        else:
            # no solution found
            return False

    def get_solutions(self) -> list:
        return self._solutions

    def get_solution(self, var) -> float:
        if isinstance(var, str):
            return self._solutions[self._variables[var].index]
        if isinstance(var, int):
            return self._solutions[var]
        if isinstance(var, LstSqSolverVar):
            return self._solutions[var.index]
        raise ValueError("Invalid variable type")

    def print(self) -> str:
        for i in range(self._n_constraints):
            print(f"{self._A[i]} = {self._b[i]}")
