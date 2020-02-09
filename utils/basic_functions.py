# Author:     Andrew Smith
# File:       basic_functions.py
# Project:    Pokemon Team Builder

'''
primitive_functions.py: This file contains a number of quality-of-life
                        functions as the foundation for future, more complex
                        functions.
'''


import json
import numpy as np


def get_weighted_stats(stats):
    '''
    Takes a stats dictionary as input and returns the weighteda ttack and
    defense.
    '''
    weighted_atk = max(stats['Atk'], stats['SpA']) * 0.85 + \
                   min(stats['Atk'], stats['SpA']) * 0.15
    weighted_def = max(stats['Def'], stats['SpD']) * 0.85 + \
                   min(stats['Def'], stats['SpD']) * 0.15
    return weighted_atk, weighted_def


def check_role(stats):
    '''
    Takes a stats dictionary as input and computes a specificrole for the
    Pokemon.  Options are {speedy_Atk, speedy_SpA, speedy_mixed, bulky_attacker,
    tank_Def, tank_SpD, tank_mixed, balanced}
    '''
    weighted_atk, weighted_def = get_weighted_stats(stats)
    if weighted_Atk > weighted_Def:
        # Do stuff here
    elif weighted_Atk < weighted_Def:
        # Do more stuff here
    else:
        return 'balanced'


def compute_power(stats, role):
    '''
    Takes a stats dictionary as input and computes a "power" based on the
    Pokemon's role and their weighted stats.  Since it's unfair to
    judge a tank by their attack and an attacker by their defense, each
    Computed Power (or CP for short) will favor a Pokemon's stats based on
    their role.
    '''


def check_compatibility(mon1, mon2):
