#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
Author: Hanyu Wang
Created time: 2023-11-17 14:19:26
Last Modified by: Hanyu Wang
Last Modified time: 2023-11-17 14:45:03
'''

import numpy as np
import xyz

def test_thetas():
    
    state_vector = np.array([1, -1])
    
    state = xyz.quantize_state(state_vector)
    
    thetas = state.get_ry_angles(0)
    
    print(thetas)
    best_theta = state.get_most_frequent_theta(0)
    
    print(best_theta)
    
if __name__ == '__main__':
    test_thetas()