# Author:     Syed Sadat Nazrul (and Andrew Smith a little bit)
# File:       pokedex_scraper.py
# Project:    Pokemon Team Builder

'''
pokedex_scraper.py: This file takes data from pokemondb and turns it into
                    pokedex data for pokedex.json.

Note: I got the base of this code thanks to this url:
https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059

As someone who is new to web scraping, it really saved my butt.
'''
# TODO: Add tier scraping support.

import requests
import lxml.html as lh
import json
import os
import os.path as osp
from bs4 import BeautifulSoup


def scrape_pokedex():
    # This void function takes Pokemon data from the pokemondb website and
    # stores it as a dictionary

    # Set the url to the full pokemondb pokedex
    url = 'http://pokemondb.net/pokedex/all'

    # Create a page to handle the contents of the website
    page_info = requests.get(url)

    # Store the contents of the website as element data
    page_element_data = lh.fromstring(page_info.content)

    # Parse data that is stored between <tr> tags in HTML
    tr_elements = page_element_data.xpath('//tr')

    # Create empty list for key names and all_pokemon dictionary for the pokedex
    col_names = []
    all_pokemon = {}

    # For each row, store each first element (header) and an empty list
    for th_tag in tr_elements[0]:
        name = th_tag.text_content()
        col_names.append(name)
        all_pokemon[name] = []

    # Since the first row is the header, iterate through remaining rows
    for j in range(1,len(tr_elements)):
        # pokemon_row is the j-th row
        pokemon_row = tr_elements[j]

        # If the row is not of size 10, the //tr data is not from our table
        if len(pokemon_row) != 10:
            print('Wrong table or bad data.')
            break

        # Iterate through each element of the row
        for i, pokemon_row_element in enumerate(pokemon_row.iterchildren()):
            data = pokemon_row_element.text_content()

            # Convert any numerical value to an int
            try:
                data = int(data)
            except:
                pass

            # Append the data to the empty list of the i-th column
            all_pokemon[col_names[i]].append(data)

    return all_pokemon


def build_pokedex(unformatted_dex, allow_megas=False):
    # Takes in an undesirably-formatted dictionary and makes a better dictionary
    # out of it and dumps the result as pokedex.json

    # Create initial variables for the Pokemon dict
    stats = [0, 0, 0, 0, 0, 0]
    pokedex = {}
    speed_dict = {}
    j = 0
    prev_id = 0

    # This variable is less self-explanatory.  It is needed so that alternate
    # forms don't overwrite the normal forms
    alt_form = False
    is_mega = False

    # Iterate through all rows and store the Pokemon data in a dict
    for i in range(len(unformatted_dex['#'])):
        # Iterate through all keys for each row
        for key in unformatted_dex.keys():
            # Start checking key cases
            if key == '#': # Number
                id = int(unformatted_dex[key][i])
                # Check if the previous id is the same as the current one.  This
                # prevents undesirable stuff such as overwriting venusaur with
                # mega venusaur's stats
                if prev_id == id:
                    alt_form = True
                    continue
                else:
                    alt_form = False
                prev_id = id

            elif key == 'Name': # Name
                # Checks if the pokemon is a mega and that megas shouldn't be
                # stored in the dex since they no longer exist :(
                name = unformatted_dex[key][i].lower()
                if 'mega' in unformatted_dex[key][i].lower() and allow_megas == False:
                    is_mega = True
                    break
                # not isalpha() avoids taking the first string in the split of
                # Pokemon like Mr. mime and Type: null, who would just be 'mr.'
                # and 'type:' if this check wasn't here
                elif not name.isalpha() or alt_form:
                    is_mega = False
                    continue
                else:
                    name = name.split()[0]
                    is_mega = False

            elif key == 'Type': # Type
                # Sorts the types in alphabetical order just for consistency
                type = sorted(unformatted_dex[key][i].lower().split())

            elif key == 'Total': # Total BST
                # BST isn't needed for now
                continue

            # The next few cases just grab each Pokemon's stats
            elif key == 'HP': # HP
                stats[0] = int(unformatted_dex[key][i])
            elif key == 'Attack': # Attack
                stats[1] = int(unformatted_dex[key][i])
            elif key == 'Defense': # Defense
                stats[2] = int(unformatted_dex[key][i])
            elif key == 'Sp. Atk': # Special Attack
                stats[3] = int(unformatted_dex[key][i])
            elif key == 'Sp. Def': # Special Defense
                stats[4] = int(unformatted_dex[key][i])
            elif key == 'Speed': # Speed
                stats[5] = int(unformatted_dex[key][i])

                # Add the Pokemon to the Pokedex
                pokedex[name] = {}
                pokedex[name]['dex_id'] = id
                pokedex[name]['type'] = type
                pokedex[name]['stats'] = stats
                pokedex[name]['alt_form'] = alt_form
                # speed_rank is initialized as -1 for all pokemon and
                # only overwritten for non-alt forms later
                pokedex[name]['speed_rank'] = -1
                if not is_mega:
                    speed_dict[name] = stats[5]

                # This is necessary for some reason otherwise every Pokemon will
                # have Eternatus's stats
                stats = [0, 0, 0, 0, 0, 0]

            # I know this one is entirely unnecessary, but I like having it here
            # for readability
            else:
                continue

    speed_dict = {k : v for k, v in sorted(speed_dict.items(), \
                  key=lambda item : item[1])}

    # Find how many Pokemon each Pokemon outspeeds
    # Initialize prev_speed as the lowest speed stat in the game
    prev_speed = 5
    mons = []
    j = 0
    count = 0
    for i, mon in enumerate(speed_dict):
        cur_speed = speed_dict[mon]

        # Add the current mon to a list of other mons with the same speed
        if cur_speed == prev_speed:
            mons.append(mon)

        else:
            # Make all mons with the same score have the same rank
            for repeat_mon in mons:
                pokedex[repeat_mon]['speed_rank'] = j
            mons = []
            j = i

            # Add the current mon to the dictionary, otherwise it will get
            # skipped
            pokedex[mon]['speed_rank'] = j
        prev_speed = cur_speed

    # Write the data to a JSON
    with open(osp.join(os.pardir, 'data', 'pokedex.json'), 'w') as f_out:
        json.dump(pokedex, f_out, indent=2)

'''This is all WIP code, but it is garbage right now'''
# def test():
#     # This void function takes Pokemon data from the pokemondb website and
#     # stores it as a dictionary
#
#     # Set the url to the full pokemondb pokedex
#     url = 'https://www.smogon.com/dex/ss/formats/ou/'
#
#     # Create a page to handle the contents of the website
#     page_info = requests.get(url)
#
#     # Store the contents of the website as element data
#     soup = BeautifulSoup(page_info.content, features='lxml')
#     script = soup.find('script').find_all(text=True, recursive=False)
#     smogon_json_text = script[0]
#     smogon_json_text = smogon_json_text.split('=')[1]
#     parsed_smogon_json = json.loads(smogon_json_text)
#     print(parsed_smogon_json)
#
#     assert False


def main():
    pokedex = scrape_pokedex()
    build_pokedex(pokedex)


if __name__ == '__main__':
    main()
    # test()
