# Author:     Syed Sadat Nazrul (and Andrew Smith a little bit)
# File:       pokedex_scraper.py
# Project:    Pokemon Team Builder

'''
pokedex_scraper.py: This file takes data from pokemondb and turns it into
                    pokedex data for pokedex.json.

Note: I got a lot of this code thanks to this url:
https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059

As someone who is new to web scraping, it really saved my butt.
'''

import requests
import lxml.html as lh
import pandas as pd
import json
import os
import os.path as osp

url='http://pokemondb.net/pokedex/all'

# Create a page to handle the contents of the website
page = requests.get(url)

# Store the contents of the website as doc
doc = lh.fromstring(page.content)

# Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')

# Create empty list
col = []
i = 0

# For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i += 1
    name = t.text_content()
    col.append((name,[]))

# Since out first row is the header, data is stored on the second row onwards
for j in range(1,len(tr_elements)):
    # T is our j'th row
    T=tr_elements[j]

    # If row is not of size 10, the //tr data is not from our table
    if len(T)!=10:
        break

    # i is the index of our column
    i=0

    # Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content()
        # Check if row is empty
        if i>0:
        # Convert any numerical value to integers
            try:
                data=int(data)
            except:
                pass
        # Append the data to the empty list of the i'th column
        col[i][1].append(data)
        # Increment i for the next column
        i+=1

Dict={title:column for (title,column) in col}
df=pd.DataFrame(Dict)

# Create initial variables for the Pokemon dict
stats = [0, 0, 0, 0, 0, 0]
pokedex = {}
j = 0
prev_id = 0

# This variable is less self-explanatory.  It is needed so that alternate forms
# don't overwrite the normal forms
alt_form = False

# Iterate through all rows and store the Pokemon data in a dict
for i in range(len(df)):
    # Iterate through all keys for each row
    for key in df.keys():
        # Start checking key cases

        if key == '#': # Number
            id = int(df[key][i])
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
            # not isalpha() avoids taking the first string in the split of
            # Pokemon like Mr. mime and type: null, who would just be mr. and
            # type: if this check wasn't here
            if not df[key][i].isalpha() or alt_form:
                name = df[key][i].lower()
            else:
                name = df[key][i].lower().split()[0]

        elif key == 'Type': # Type
            # Sorts the types in alphabetical order just for consistency
            type = sorted(df[key][i].lower().split())

        elif key == 'Total': # Total BST
            # BST isn't needed for now
            continue

        # The next few cases just grab each Pokemon's stats
        elif key == 'HP': # HP
            stats[0] = int(df[key][i])
        elif key == 'Attack': # Attack
            stats[1] = int(df[key][i])
        elif key == 'Defense': # Defense
            stats[2] = int(df[key][i])
        elif key == 'Sp. Atk': # Special Attack
            stats[3] = int(df[key][i])
        elif key == 'Sp. Def': # Special Defense
            stats[4] = int(df[key][i])
        elif key == 'Speed': # Speed
            stats[5] = int(df[key][i])

            # Add the Pokemon to the Pokedex
            pokedex[name] = {}
            pokedex[name]['dex_id'] = id
            pokedex[name]['type'] = type
            pokedex[name]['stats'] = stats
            pokedex[name]['alt_form'] = alt_form

            # This is necessary for some reason otherwise every Pokemon will
            # have Eternatus's stats
            stats = [0, 0, 0, 0, 0, 0]

        # I know this one is entirely unnecessary, but I like having it here
        else:
            continue

# Write the data to a JSON
with open(osp.join(os.pardir, 'data', 'pokedex.json'), 'w') as f_out:
    json.dump(pokedex, f_out, indent=2)
