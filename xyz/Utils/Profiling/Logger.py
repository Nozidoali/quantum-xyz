#!/usr/bin/env python
# -*- encoding=utf8 -*-

"""
Author: Hanyu Wang
Created time: 2023-06-25 11:07:26
Last Modified by: Hanyu Wang
Last Modified time: 2023-06-25 11:09:58
"""

import logging


def add_log(logger: logging.Logger):
    def decorator(func):
        def newFunc(*args, **kwargs):
            ret = func(*args, **kwargs)
            return ret

        return newFunc

    return decorator
