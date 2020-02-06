# Author:     Andrew Smith
# File:       execute_builder.py
# Project:    Pokemon Team Builder

'''
execute_builder.py: This file is the main execution file.
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
    parser.add_argument('--results', required=True, \
                        help='path to the results file')
    parser.add_argument('--test_flag', action='store_true', \
                        help='flag to make main run as a test')
    parser.add_argument('--find_partner_flag', action='store_true', \
                        help='flag to make main find a partner pokemon')
    parser.add_argument('--build_team_flag', action='store_true', \
                        help='flag to make main build a team')
    parser.add_argument('--mons', nargs='+', \
                        help='one or more pokemon to use for the algorithm. ' +\
                        'use one for find_partner and one or more for' +\
                        'build_team.')
    args = parser.parse_args()
    return args

def load_data(data_path):
    # This function takes in a data path as the argument and loads the pokemon
    # and type data jsons
    print('Loading data...')

    # Loads the pokedex database
    with open(osp.join(data_path, 'pokedex.json')) as f_in:
        pokemon = json.load(f_in)

    # Loads type data (weaknesses, resistances, immunities)
    with open(osp.join(data_path, 'type_data.json')) as f_in:
        types = json.load(f_in)

    print('Finished loading data.')
    return pokemon, types

def find_partner(mon, dex):
    # This function takes in a single pokemon as a string and finds a partner
    # that covers its flaws
    print('Searching for a partner for {}.'.format(mon))
    partners = {}

    # Iterate through the pokedex dict and calculate the type synergy of each
    # pair
    for count, pokemon in enumerate(dex.keys()):
        partners[pokemon] = type_synergy(dex[mon]['type'], dex[pokemon]['type'])
        if count % 100 == 0:
            print('Done with {} Pokemon.'.format(count))

    # Sort the dictionary by type synergy value
    partners = {k : v for k, v in sorted(partners.items(), \
               key=lambda item: item[1])}

    # Only display the first ten pokemon in partners
    for count, pokemon in enumerate(partners.keys()):
        if count == 10:
            break
        else:
            print('|{} \t|\t {} \t|\t Score = {:.5f} \t|'.format(count + 1, \
                  pokemon, round(partners[pokemon], 5)))
    return

def main(data, results='../dumps/results.txt', mons=[], test_flag=False, \
         find_partner_flag=False, build_team_flag=False):
    # Main execution function.  Check each flag and execute the chosen one.
    if test_flag is True:
        test(dex)
    elif find_partner_flag is True:
        dex, type_data = load_data(data)
        find_partner(mons[0], dex)
    elif build_team_flag is True:
        dex, type_data = load_data(data)
        build_team(mons, dex)
    else:
        print("No option selected.  Please choose test, find_partner, or ", \
              "build team.\n")
    return

if __name__ == '__main__':
    args = parse_arguments()
    main(args.data, args.results, args.mons, args.test_flag, \
         args.find_partner_flag, args.build_team_flag)
