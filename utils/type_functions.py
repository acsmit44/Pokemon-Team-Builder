# Author:     Andrew Smith
# File:       type_functions.py
# Project:    Pokemon Team Builder

'''
type_functions.py: This file contains functions that handle the encoding and
                   decoding of types.
'''

import json
import numpy as np
from numpy.linalg import norm
import os
import os.path as osp

# Global variable for what index each type has
type_indices = ['bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', \
                'fire', 'flying', 'ghost', 'grass', 'ground', 'ice', \
                'normal', 'poison', 'psychic', 'rock', 'steel', 'water']


def get_wri(type):
    # Takes in a single type and type dict and returns the weaknesses,
    # resistances, and immunities for it.

    with open(osp.join(os.pardir, 'new_data', 'type_data.json')) as f_in:
        data = json.load(f_in)

    # Create neutral type list
    full_type_wri = [1 for i in range(18)]

    # Change all weaknesses to 2, for x2 damage
    for weakness in data[type]['weaknesses']:
        full_type_wri[type_indices.index(weakness)] = 2

    # Change all resistances to 1/2, for x1/2 damage
    for resistance in data[type]['resistances']:
        full_type_wri[type_indices.index(resistance)] = 1/2

    # Change all immunities to 0, for x0 damage
    for immunity in data[type]['immunities']:
        full_type_wri[type_indices.index(immunity)] = 0

    return full_type_wri # A list of the weaknesses and resistances


def build_wri(types):
    # Takes in the type list as an argument and returns the weaknesses,
    # resistances, and immunities of the Pokemon as a list.
    if len(types) == 2:
        return [x*y for x, y in zip(get_wri(types[0]), \
                get_wri(types[1]))]
    else:
        return get_wri(types[0])


def type_synergy(types_1, types_2):
    # Takes in two type lists, performs element-wise multiplication on them, and
    # finds the 2-norm of the resulting vector

    # Find the weaknesses, resistances, and immunities vector of the two mons
    # together
    wri = np.asarray([x*y for x, y in zip(build_wri(types_1), \
                      build_wri(types_2))])

    # Return the norm of the wri vector, which we want to minimize
    return norm(wri) # TODO: Test other orders of norms, blow up with common
                     # weaknesses
