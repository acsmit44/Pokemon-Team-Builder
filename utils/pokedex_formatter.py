# Author:  Andrew Smith
# File:    pokedex_formatter.py
# Project: Pokemon Team Builder

'''
pokedex_formatter.py: Using the pokedex.json repository from
                      https://github.com/fanzeyi/pokemon.json, this script will
                      reformat the list as a dictionary keyed by the pokemon
                      names themselves.
'''

import json
import argparse
import os
import os.path as osp


def reformat_types(types):
    # Takes a types list with weaknesses and such as input and returns a new
    # types dictionary with sets instead of lists.
    new_types = {}
    for type in types:
        new_types[type['type']] = {'weaknesses' : [weak.lower() for weak in \
                                                  type['weaknesses']], \
                                   'resistances' : [res.lower() for res in \
                                                   type['resistances']], \
                                   'immunities' : [none.lower() for none in \
                                                  type['no_effect']]}
    return new_types


def reformat_pokedex(pokedex):
    pokemon = {}
    for progress, mon in enumerate(pokedex):
        stats = [mon['base']['HP'], \
                 mon['base']['Attack'], \
                 mon['base']['Defense'], \
                 mon['base']['Sp. Attack'], \
                 mon['base']['Sp. Defense'], \
                 mon['base']['Speed']]
        pokemon[mon['name']['english']] = {'dex_id' : mon['id'], \
                                           'type' : sorted([type.lower() for type in mon['type']]), \
                                           'stats' : stats}
        if progress % 100 == 0:
            print('Done with {} Pokemon.'.format(progress))
    print('Reformatting done.')
    return pokemon


if __name__ == '__main__':
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old_data', required=True, \
                        help='path to the pokedex.json folder')
    parser.add_argument('--new_data', required=True, \
                        help='path to the new pokedex data folder')
    args = parser.parse_args()

    # Load types and pokedex data.
    print('Loading old data files...')
    with open(osp.join(args.old_data, 'pokemon.json', 'types.json')) as f_in:
        types = json.load(f_in)
    with open(osp.join(args.old_data, 'pokemon.json', 'pokedex.json')) as f_in:
        pokedex = json.load(f_in)

    # Call functions to reformat data.
    print('Reformatting data...')
    types = reformat_types(types)
    pokedex = reformat_pokedex(pokedex)
    avg_stats, std_dev_stats = stats_analysis(pokedex)
    print("Average stats = \n", avg_stats)
    print("Standard deviation of stats = \n", std_dev_stats)

    # Make a new directory for the updated data if one doesn't already exist.
    os.makedirs(args.new_data, exist_ok=True)
    # Open files in the new directory and dump updated data.
    print('Writing new data...')
    with open(osp.join(args.new_data, 'types.json'), 'w') as f_out:
        json.dump(types, f_out, indent=2)
    with open(osp.join(args.new_data, 'pokemon.json'), 'w') as f_out:
        json.dump(pokedex, f_out, indent=2)
