# Author:     Andrew Smith
# File:       run_team_builder.py
# Project:    Pokemon Team Builder

'''
run_team_builder.py: This file is the main execution file.
'''

import json
import argparse
import os
import os.path as osp
from type_functions import type_synergy

def parse_arguments():
    # Void that creates some arguments to be passed into the main function

    # Create argument parser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, \
                        help='path to the data directory')
    parser.add_argument('--results_path', required=True, \
                        help='path to the results file')
    parser.add_argument('--test_flag', action='store_true', \
                        help='flag to make main run as a test')
    parser.add_argument('--find_partner_flag', action='store_true', \
                        help='flag to make main find a partner pokemon')
    parser.add_argument('--build_team_flag', action='store_true', \
                        help='flag to make main build a team')
    parser.add_argument('--mons', nargs='+', type=str.lower, \
                        help='one or more pokemon to use for the algorithm. ' +\
                        'use one for find_partner and one or more for' +\
                        'build_team.')
    args = parser.parse_args()
    return args

def load_data(data_path):
    # This function takes in a data path as the argument and loads the pokemon
    # and type data jsons
    print('Loading data...')

    # Loads the pokedex data
    with open(osp.join(data_path, 'pokedex.json')) as f_in:
        pokemon = json.load(f_in)

    # Loads type data (weaknesses, resistances, immunities)
    with open(osp.join(data_path, 'type_data.json')) as f_in:
        types = json.load(f_in)

    print('Finished loading data.')
    return pokemon, types

def save_results(path_string, scores, mon):
    # Takes the results from the team builder or partner finder function and
    # writes the results to a text file

    # Find the longest string in the scores dict, used for prettier output
    max_len = 0
    for key in scores.keys():
        if len(key) > max_len:
            max_len = len(key)

    # Open the user-specified file and write the scores output
    with open(path_string, 'w') as f_out:
        f_out.write('Results for {}:\n'.format(mon))
        f_out.write('-' * (max_len + 31))
        f_out.write('\n')
        for count, pokemon in enumerate(scores):
            f_out.write('|  {}\t|'.format(count + 1))
            # Add more spaces to make the output prettier
            spaces = ' ' * (max_len - len(pokemon))
            f_out.write('  {}\t|'.format(pokemon + spaces))
            # Write the scores to 6 sig figs
            f_out.write('  Score = {:.5f}\t|\n'.format(scores[pokemon]))
        f_out.write('-' * (max_len + 31))
    return

def find_partner(mon, dex, results_path):
    # This function takes in a single pokemon as a string and finds a partner
    # that covers its flaws
    print('Searching for a partner for {}.'.format(mon))
    partners = {}

    # Iterate through the pokedex dict and calculate the type synergy of each
    # pair
    for count, pokemon in enumerate(dex.keys()):
        partners[pokemon] = type_synergy(dex[mon]['type'], dex[pokemon]['type'])
        if count % 150 == 0:
            print('Done with {} Pokemon.'.format(count))

    # Sort the dictionary by type synergy value
    partners = {k : v for k, v in sorted(partners.items(), \
                key=lambda item: item[1])}

    # Take only the first 10 items of the dictionary
    partners_new = {}
    for count, pokemon in enumerate(partners.keys()):
        partners_new[pokemon] = partners[pokemon]
        if count == 9:
            break

    # Save results and end the function
    save_results(results_path, partners_new, mon)
    return

def main(data, results_path, mons=[], test_flag=False, \
         find_partner_flag=False, build_team_flag=False):
    # Main execution function.  Check each flag and execute the chosen one.
    if test_flag is True:
        test(dex)
    elif find_partner_flag is True:
        dex, type_data = load_data(data)
        find_partner(mons[0], dex, results_path)
    elif build_team_flag is True:
        dex, type_data = load_data(data)
        build_team(mons, dex)
    else:
        print("No option selected.  Please choose test, find_partner, or ", \
              "build team.\n")
    return

if __name__ == '__main__':
    args = parse_arguments()
    main(args.data, args.results_path, args.mons, args.test_flag, \
         args.find_partner_flag, args.build_team_flag)
