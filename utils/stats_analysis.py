# Author:     Andrew Smith
# File:       stats_analysis.py
# Project:    Pokemon Team Builder

'''
stats_analysis.py: This file performs an elementary statistical analysis on all
                   Pokemon stats in the pokedex.json file.  It finds information
                   such as stat averages and standard deviation.
'''

import json
import numpy as np
from numpy.linalg import norm
from math import sqrt

def get_avg_std(pokedex):
    # This function takes in the pokedex dict and computes various useful info
    # such as average stats and standard deviation

    # Creates an mx6 matrix of Pokemon stats where m is the number of Pokemon in
    # the pokedex
    for count, mon in enumerate(pokedex.keys()):
        if count == 0:
            stats_vec = np.asarray(pokedex[mon]['stats'])
            stats_vec = stats_vec.reshape(1,6)
        else:
            stat_vec = np.asarray(pokedex[mon]['stats'])
            stat_vec = stat_vec.reshape(1,6)

            stats_vec = np.concatenate((stats_vec, stat_vec))

    # Finds the number of Pokemon in the pokedex
    num_mons = stats_vec.shape[0]

    # Transposes the stats_vec so that the rows are the stats and then sums them
    # and divides by the number of Pokemon to find the average
    avg_vec = np.asarray([sum(row) / num_mons for row in stats_vec.T])

    # Does the same thing as above but finds standard deviation instead
    std_vec = [sqrt(norm(row - avg_vec[i])**2 / num_mons - 1) for i, row in \
                         enumerate(stats_vec.T)]

    return avg_vec, std_vec


def test():
    with open('../data/pokedex.json') as f_in:
        pokedex = json.load(f_in)
    avg_vec, std_vec = get_avg_std(pokedex)
    print('The average vec is: {}\nThe std vec is: {}'.format(avg_vec, std_vec))

if __name__ == '__main__':
    test()
