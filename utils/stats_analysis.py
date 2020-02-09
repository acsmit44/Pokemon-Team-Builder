# Author:     Andrew Smith
# File:       stats_analysis.py
# Project:    Pokemon Team Builder

'''
stats_analysis.py: This file performs an elementary statistical analysis on all
                   Pokemon stats in the pokedex.json file.  It finds information
                   such as stat averages and standard deviation.
'''

import json
import os
import os.path as osp
import numpy as np
from numpy.linalg import norm
from math import sqrt
import matplotlib.pyplot as plt


def make_stats_matrix(pokedex):
    # Creates an mx6 matrix of Pokemon stats where m is the number of Pokemon in
    # the pokedex and counts the number of mons
    num_mons = len(pokedex)
    prev_id = 0
    stats_matrix = []
    for count, mon in enumerate(pokedex.keys()):
        # Make the first 5 indices the normal stats and set the sixth to
        # the speed rank
        stat_list = pokedex[mon]['stats'][:5]
        stat_list.append((pokedex[mon]['speed_rank'] + 1) / num_mons)
        stats_matrix.append(stat_list)
    stats_matrix = np.asarray(stats_matrix)

    # Fixes the stats matrix to more accurately reflect the in-game stats of
    # Pokemon at level 100 (see the PDF for a deeper explanation)
    for stat_index, row in enumerate(stats_matrix.T):
        # Change base HP to (HP * 2 + 141)
        if stat_index == 0:
            stats_matrix[:, stat_index] = row * 2 + 141
        # Change every other stat to (stat * 2 + 36)
        elif stat_index < 5:
            stats_matrix[:, stat_index] = row * 2 + 36
    print(stats_matrix)
    return stats_matrix, num_mons


def get_role_data(stats_matrix):
    # This function takes in a corrected mx6 stats matrix and uses it to find
    # each Pokemon's strengths, i.e. physical/special offense, physical/special
    # durability, etc.
    phys_off = stats_matrix[:, 1] * stats_matrix[:, 5]
    spec_off = stats_matrix[:, 3] * stats_matrix[:, 5]
    phys_def = stats_matrix[:, 0] * stats_matrix[:, 2]
    spec_def = stats_matrix[:, 0] * stats_matrix[:, 4]


def get_mean_std(data_matrix, samples):
    # This function takes in a matrix of mxn size and computes the standard
    # deviation and mean of the data.

    # Transposes the data_matrix so that the rows are the stats and then sums
    # them and divides by the number of samples to find the average
    mean_vec = np.asarray([sum(row) / samples for row in data_matrix.T])

    # Does the same thing as above but finds standard deviation instead
    std_vec = np.asarray([sqrt(norm(row - mean_vec[i])**2 / samples) for \
                         i, row in enumerate(data_matrix.T)])

    return mean_vec, std_vec


def standard_score(data_matrix, mean_vec, std_vec):
    # This function takes in a stats matrix and standardizes it based on
    # (X - mu) / sigma then returns the mxn matrix

    standard_matrix = np.asarray([(row - mean_vec[i]) / std_vec[i] for i, row \
                                  in enumerate(data_matrix.T)])
    return standard_matrix.T


def plot_stats(stats_matrix, binwidth=6):
    # Creates a distribution plot for all stats
    stat_names = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', \
                  'Speed']

    for i, stat_name in enumerate(stat_names):

        # Set up the subplot
        cur = plt.subplot(3, 2, i + 1)

        # Grab the current stat vector from the stats matrix
        stat_list = list(stats_matrix[:, i])

        # Find the stat range for the plot
        stat_range = max(stat_list) - min(stat_list)

        # Create matplotlib histogram
        cur.hist(stat_list, color = 'blue', edgecolor = 'black',
                 bins = 100)

        # Add labels
        cur.set_title('Distribution of Pokemon {} stats'.format(stat_name))
        cur.set_xlabel('Stat range (standard deviations away from the mean)')
        cur.set_ylabel('Number of mons in range')

    plt.tight_layout()
    plt.show()


def main(do_plot=False):
    with open(osp.join(os.pardir, 'data', 'pokedex.json')) as f_in:
        pokedex = json.load(f_in)
    stats_matrix, num_mons = make_stats_matrix(pokedex)
    mean_vec, std_vec = get_mean_std(stats_matrix, num_mons)
    standard_matrix = standard_score(stats_matrix, mean_vec, std_vec)
    if do_plot:
        plot_stats(standard_matrix)
    print('The mean vec is: {}\nThe std vec is: {}'.format(mean_vec, std_vec))


if __name__ == '__main__':
    main()
