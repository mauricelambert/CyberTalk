#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    CyberAttackSimulation for CyberTalk
#    Copyright (C) 2025  CyberAttackSimulation

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
"""

from sys import setrecursionlimit, getrecursionlimit, exit
from itertools import permutations
from string import punctuation
from datetime import datetime
from hashlib import sha256
from time import time
from math import log2

MAX_COMBINATION_LENGTH = 3
MINIMUM_LENGTH = 6
MAXIMUM_LENGTH = 25

leet_map = str.maketrans({
    'a': '@', 'A': '@',
    'o': '0', 'O': '0',
    'i': '1', 'I': '1',
    'l': '1', 'L': '1',
    's': '$', 'S': '$',
    'e': '3', 'E': '3',
    't': '7', 'T': '7'
})

special_symbols = list("!@#$%^&*()-_=+[]{};:,.<>?/|~")

def input_list(prompt):
    s = input(prompt + " (séparer par des virgules, laisser vide si aucun): ").strip()
    return [x.strip() for x in s.split(",") if x.strip()]

def ask_basic():
    firsts = input_list("Prénoms")
    lasts = input_list("Noms de famille")
    pets = input_list("Noms d'animaux")
    nicks = input_list("Surnoms / pseudos")
    others = input_list("Autres mots (lieux, équipes, hobbies)")
    dob = input("Date de naissance (JJ/MM/AAAA), année (AAAA) ou années si estimées (AAAA-AAAA), laisser vide si non: ").strip()
    lucky = input_list("Nombres porte-bonheur (ex: 7, 13, 1984)")
    return {
        "firsts": firsts,
        "lasts": lasts,
        "pets": pets,
        "nicks": nicks,
        "others": others,
        "dob": dob,
        "lucky": lucky
    }

def normalize_dates(data, tokens):
    years = []
    base_year = None
    
    dob = data.get('dob', '')
    if dob:
        parts = dob.replace('-', '/').split('/')
        if len(parts) == 1 and parts[0].isdigit():
            # if len(tokens) == 4:
            #     tokens.append(parts[0][-2:])
            tokens.append(parts[0])
        elif len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            if len(parts[0]) == 4 and len(parts[1]) == 4:
                base_year = parts[0]
                tokens.append(parts[0])
                for year in range(int(parts[0]), int(parts[1]) + 1):
                    years.append(str(year))
        else:
            for p in parts:
                if p.strip().isdigit():
                    tokens.append(p.strip())

            if len(parts) >= 3 and all(p.strip().isdigit() for p in parts[:3]):
                dd, mm, yyyy = parts[0].zfill(2), parts[1].zfill(2), parts[2]
                tokens.append(dd+mm+yyyy)
                tokens.append(yyyy+mm+dd)
                tokens.append(mm+dd)
                tokens.append(dd+mm)
    
    return years, base_year

def normalize_tokens(data):
    """
    Transforme les saisies en token de base.
    """

    tokens = []
    names = {}
    associated_names = {}

    for k in ['firsts','lasts','pets','nicks','others']:
        if new_tokens := data.get(k):
            tokens.extend(new_tokens)
            for token in new_tokens:
                if len(token) > 2:
                    names[token] = token[:2]
 
    if (firsts := data.get('firsts')) and (lasts := data.get('lasts')):
        for first in firsts:
            for last in lasts:
                associated_names[(first, last)] = (first[0] + last[0], last[0] + first[0])

    years, base_year = normalize_dates(data, tokens)
    
    tokens += data.get('lucky', [])

    tokens = [t for t in dict.fromkeys(tokens) if len(t) >= 1]
    return tokens, names, associated_names, years, base_year

def transformations2(tokens, from_=[]):
    if 1 not in from_:
        outs = set()
        for token in tokens:
            for s in ['!', '@', '#', '$']:
                outs.add(s + token)
                outs.add(token + s)
        yield outs
        yield from transformations2(outs, from_ + [1])

    if 2 not in from_:
        outs = set()
        for token in tokens:
            for s in range(10):
                outs.add(token + str(s))
                outs.add(str(s) + token)
        yield outs
        yield from transformations2(outs, from_ + [2])

        outs = set()
        for token in tokens:
            for s in range(100):
                outs.add(token + str(s).rjust(2, "0"))
                outs.add(str(s).rjust(2, "0") + token)
        yield outs
        yield from transformations2(outs, from_ + [2])

def transformations(token):
    """
    Génère variantes d'un token (caps, leet, reversed, doubles).
    """

    outs = set()
    outs.add(token)
    outs.add(token.lower())
    outs.add(token.capitalize())
    outs.add(token.upper())
    outs.add(token[::-1])

    outs.add(token.translate(leet_map))
    outs.add(token.capitalize().translate(leet_map))

    for new in list(transformations2(outs)):
        outs.update(new)
    
    return outs

# def estimate_entropy(pwd):
#     size = 0
#     if any(c.islower() for c in pwd): size += 26
#     if any(c.isupper() for c in pwd): size += 26
#     if any(c.isdigit() for c in pwd): size += 10
#     if any(c in punctuation for c in pwd): size += len(punctuation)
#     if size == 0:
#         size = 1
#
#     entropy = len(pwd) * log2(size)
#     return entropy
    
counter = 0
seen = set()
    
def handle_combo(combo, names, associated_names, base_year, years, site_tag, from_=[]):
    if handle_base(''.join(combo), site_tag):
        return

    if 1 not in from_ and base_year and base_year in combo:
        for year in years:
            combo1 = list(combo)
            combo1[combo.index(base_year)] = year
            handle_combo(tuple(combo1), names, associated_names, base_year, years, site_tag, from_ + [1])
                    
    if 2 not in from_:
        combos = {combo}
        while combos:
            combo0 = combos.pop()
            for name, value in names.items():
                if name in combo0:
                    combo1 = list(combo0)
                    combo1[combo.index(name)] = value
                    combo1 = tuple(combo1)
                    combos.add(combo1)
                    handle_combo(combo1, names, associated_names, base_year, years, site_tag, from_ + [2])
    
    if 3 not in from_:
        for (first, last), (_1, _2) in associated_names.items():
            if last not in combo and first in combo:
                index_first = combo.index(first)
                combo1 = list(combo)
                combo1[index_first] = _1
                handle_combo(tuple(combo1), names, associated_names, base_year, years, site_tag, from_ + [3])
                combo1 = list(combo)
                combo1[index_first] = _2
                handle_combo(tuple(combo1), names, associated_names, base_year, years, site_tag, from_ + [3])
            elif last in combo and first not in combo:
                index_last = combo.index(last)
                combo1 = list(combo)
                combo1[index_last] = _1
                handle_combo(tuple(combo1), names, associated_names, base_year, years, site_tag, from_ + [3])
                combo1 = list(combo)
                combo1[index_last] = _2
                handle_combo(tuple(combo1), names, associated_names, base_year, years, site_tag, from_ + [3])

def handle_base(base, site_tag):
    if hash(base) in seen:
        return True
    global counter
    seen.add(hash(base))
    vars = transformations(base)
    cand_list = set()
    for v in vars:
        cand_list.update({v,
                     v.capitalize(),
                     v.upper(),
                     v.lower()})
                         
        if site_tag:
            cand_list.add(site_tag + v)
            cand_list.add(v + site_tag)

    for cand in cand_list:
        if MAXIMUM_LENGTH > len(cand) > MINIMUM_LENGTH:
            counter += 1
            if sha256(cand.encode()).hexdigest() == 'a253b1985e9a89f7c3fd9777c5d7f4059c0b7bc169c2b65ba328c784f62bc28a':
                print("Password found:", cand)

def generate_passwords(tokens, names, associated_names, base_year, years, site_tag=None):
    # save = getrecursionlimit()
    # setrecursionlimit(1000000)
    for r in range(1, MAX_COMBINATION_LENGTH + 1):
        combos = permutations(tokens, r)
        for combo in combos:
            handle_combo(combo, names, associated_names, base_year, years, site_tag)
    # setrecursionlimit(save)

def main():
    data = ask_basic()
    tokens, names, associated_names, years, base_year = normalize_tokens(data)
    if not tokens:
        print("Aucun token fourni. Sortie.")
        #exit(1)

    site_tag = input("Tag lié au service (ex: gmail, amazon) — optionnel: ").strip()

    print("\nGénération en cours...")
    start = time()
    pwds = generate_passwords(tokens, names, associated_names, base_year, years, site_tag=site_tag or None)
    end = time()

    print(f"{counter} candidats générés en {end - start:.2f} seconde.")

#     for p, e in pwds:
#         print(f"{p}  —  {e:.1f} bits")

    print_pwds = input("\nAfficher les résultats dans la console ? (o/N): ").strip().lower()
    if print_pwds == 'o':
        for p in pwds:
            print(p)

    save = input("\nEnregistrer les résultats dans un fichier ? (o/N): ").strip().lower()
    if save == 'o':
        fname = f"pwds_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fname, 'w', encoding='utf-8') as f:
#             for p, e in pwds:
#                 f.write(f"{p}\t{e:.1f}\n")
            for p in pwds:
                f.write(p)
        print(f"Sauvegardé dans {fname} (stockage local).")

if __name__ == "__main__":
    main()
