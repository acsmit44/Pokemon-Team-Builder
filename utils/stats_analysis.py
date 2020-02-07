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
import matplotlib.pyplot as plt


def make_stats_matrix(pokedex, ignore_alt_forms=True):
    # Creates an mx6 matrix of Pokemon stats where m is the number of Pokemon in
    # the pokedex and counts the number of mons
    prev_id = 0
    speed_dict = {}
    for count, mon in enumerate(pokedex.keys()):
        if count == 0:
            stats_matrix = np.asarray(pokedex[mon]['stats'])
            stats_matrix = stats_matrix.reshape(1,6)
            speed_dict[mon] = pokedex[mon]['stats'][5]

        # Check if the Pokemon is an alt form and that they are to be ignored
        elif pokedex[mon]['alt_form'] == False or ignore_alt_forms == False:
            stat_vec = np.asarray(pokedex[mon]['stats'])
            stat_vec = stat_vec.reshape(1,6)
            speed_dict[mon] = pokedex[mon]['stats'][5]
            stats_matrix = np.concatenate((stats_matrix, stat_vec))
        else:
            continue

    # Finds the number of Pokemon in the pokedex
    num_mons = max(stats_matrix.shape)

    return stats_matrix, num_mons


def get_avg_std(pokedex):
    # This function takes in the pokedex dict and computes various useful info
    # such as average stats and standard deviation

    # Get the stats matrix and number of Pokemon in it
    stats_matrix, num_mons = make_stats_matrix(pokedex)

    # Transposes the stats_matrix so that the rows are the stats and then sums them
    # and divides by the number of Pokemon to find the average
    avg_vec = np.asarray([sum(row) / num_mons for row in stats_matrix.T])

    # Does the same thing as above but finds standard deviation instead
    std_vec = np.asarray([sqrt(norm(row - avg_vec[i])**2 / num_mons - 1) for \
                         i, row in enumerate(stats_matrix.T)])

    return avg_vec, std_vec


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
        cur.set_xlabel('Stat range')
        cur.set_ylabel('Number of mons in range')

    plt.tight_layout()
    plt.show()


def standard_score(stats_matrix, avg_vec, std_vec):
    # This function takes in a stats matrix and standardizes it based on
    # (X - mu) / sigma then returns the mx6 matrix
    if stats_matrix.shape[0] == 6:
        stats_matrix = stats_matrix.T

    standard_matrix = np.asarray([(row - avg_vec[i]) / std_vec[i] for i, row \
                                  in enumerate(stats_matrix.T)])
    return standard_matrix.T


def main():
    with open('../data/pokedex.json') as f_in:
        pokedex = json.load(f_in)
    avg_vec, std_vec = get_avg_std(pokedex)
    stats_matrix, _ = make_stats_matrix(pokedex)
    # plot_stats(stats_matrix)
    standard_matrix = standard_score(stats_matrix, avg_vec, std_vec)
    plot_stats(standard_matrix)
    print('The average vec is: {}\nThe std vec is: {}'.format(avg_vec, std_vec))


if __name__ == '__main__':
    main()
