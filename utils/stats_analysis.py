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
from math import sqrt, exp
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
        # Change every stat except HP and Speed to (stat * 2 + 36)
        elif stat_index < 5:
            stats_matrix[:, stat_index] = row * 2 + 36

    return stats_matrix, num_mons


def get_role_data(stats_matrix):
    # This function takes in a corrected mx6 stats matrix and uses it to find
    # each Pokemon's strengths, i.e. physical/special durability,
    # physical/special offensiveness, etc.
    num_mons = max(stats_matrix.shape)
    phys_dur = stats_matrix[:, 0] * stats_matrix[:, 2]
    spec_dur = stats_matrix[:, 0] * stats_matrix[:, 4]
    phys_off = stats_matrix[:, 1] * ((stats_matrix[:, 1] * \
               sigmoid(stats_matrix[:, 5]) + 450) / (stats_matrix[:, 1] * \
               (1 - sigmoid(stats_matrix[:, 5])) + 450))
    spec_off = stats_matrix[:, 3] * ((stats_matrix[:, 3] * \
               sigmoid(stats_matrix[:, 5]) + 450) / (stats_matrix[:, 3] * \
               (1 - sigmoid(stats_matrix[:, 5])) + 450))

    phys_dur = np.reshape(phys_dur, (num_mons, 1))
    spec_dur = np.reshape(spec_dur, (num_mons, 1))
    phys_off = np.reshape(phys_off, (num_mons, 1))
    spec_off = np.reshape(spec_off, (num_mons, 1))

    # | PD | SD | PO | SO |
    stat_rankings = np.concatenate((phys_dur, spec_dur, phys_off, spec_off), \
                                    axis=1)

    # Standardize the stats so the later calculations are more consistent
    stat_rankings = standard_score(stat_rankings, new_std=25)

    # Find the overall rankings and then normalize them
    overall_bst_ranking = np.asarray([sum(row) for row in stat_rankings])
    overall_bst_ranking = np.reshape(overall_bst_ranking, (num_mons, 1))
    overall_bst_ranking = min_max_data(overall_bst_ranking, b=num_mons)

    # Create a list for the biases
    biases = []
    for i, row in enumerate(stat_rankings):
        # Subtract the max offensiveness stat from the max durability stat. A
        # more negative score means a pokemon is more offensively biased and a
        # more positive score means it is defensively biased
        off_dur_bias = (max(row[:2]) - max(row[2:]))

        # Find the difference between the special stats and the physical stats.
        # A more negative score means a pokemon is specially biased and a more
        # positive score means it is physicall biased
        phys_spec_bias = row[0] + row[2] - (row[1] + row[3])
        biases.append([off_dur_bias, phys_spec_bias])

    # Normalize the biases to have a mean of 0 and standard deviation of 5
    biases = standard_score(np.asarray(biases), new_std=5)

    # Concatenate the biases to the rankings
    stat_rankings = np.concatenate((stat_rankings, biases, \
                                    overall_bst_ranking), axis=1)

    return stat_rankings


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


def min_max_data(data_matrix, a=1, b=100):
    # This function takes in a matrix and normalizes the data by using the
    # min-max method
    data_matrix = data_matrix.T
    for i, row in enumerate(data_matrix):
        data_matrix[i, :] = a + ((row - min(row)) * (b - a)) / \
                            (max(row) - min(row))

    return data_matrix.T


def standard_score(data_matrix, new_mean=0, new_std=1):
    # This function takes in a stats matrix and standardizes it based on
    # (X - mu) / sigma then returns the mxn matrix

    # Get the mean and standard deviation
    mean_vec, std_vec = get_mean_std(data_matrix, max(data_matrix.shape))

    standard_matrix = np.asarray([(new_mean + new_std * ((row - mean_vec[i]) / \
                                  std_vec[i])) for i, row in \
                                  enumerate(data_matrix.T)])
    return standard_matrix.T


def sigmoid(x, shift=0.45, stretch=5.5):
    # This function is a shifted sigmoid function that is modified to fit into
    # [0, 1] so that it can be used on the speed ranking of each mon.
    for i in range(max(x.shape)):
        x[i] = 1 / (1 + exp(-(stretch * (x[i] - shift))))
    return x


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


def save_results(path_string, pokedex, data_matrix):
    # Takes the results from the analysis and stores it as a simple text file
    # for human readability.  Not meant to store data for later use.

    # Find the longest pokemon name, used for prettier output
    max_len = 0
    for key in pokedex.keys():
        if len(key) > max_len:
            max_len = len(key)

    # Open the user-specified file and write the scores output
    with open(path_string, 'w') as f_out:
        f_out.write('-' * (max_len + 31))
        f_out.write('\n')
        for i, pokemon in enumerate(pokedex):
            f_out.write('|{}\t|'.format(i + 1))
            # Add more spaces to make the output prettier
            spaces = ' ' * (max_len - len(pokemon))
            f_out.write(' {}|\n'.format(pokemon + spaces))
            # Write the scores to 6 sig figs
            f_out.write('| PD = {:.5f}\t|'.format(data_matrix[i, 0]))
            f_out.write(' SD = {:.5f}\t|'.format(data_matrix[i, 1]))
            f_out.write(' PO = {:.5f}\t|'.format(data_matrix[i, 2]))
            f_out.write(' SO = {:.5f}\t|'.format(data_matrix[i, 3]))
            f_out.write(' ODB = {:.5f}\t|'.format(data_matrix[i, 4]))
            f_out.write(' PSB = {:.5f}\t|'.format(data_matrix[i, 5]))
            f_out.write(' BSR = {:.5f}\t|\n'.format(data_matrix[i, 6]))
        f_out.write('-' * (max_len + 31))
    return


def main(do_plot=False):
    with open(osp.join(os.pardir, 'data', 'pokedex.json')) as f_in:
        pokedex = json.load(f_in)
    stats_matrix, num_mons = make_stats_matrix(pokedex)
    mean_vec, std_vec = get_mean_std(stats_matrix, num_mons)
    roles = get_role_data(stats_matrix)
    save_results('../dumps/roles.txt', pokedex, roles)
    if do_plot:
        standard_matrix = standard_score(stats_matrix)
        plot_stats(standard_matrix)


if __name__ == '__main__':
    main()
