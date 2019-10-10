#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
from orace import Race
from brikkesys import Database

def main():
    race_number = 153
    os = 'linux'
    db = Database('local','linux')
    poengo = Race(db, race_number, os)
    poengo.get_names()
    names = poengo.runners
    poster = [31,32,34]
    for name in names:
        text = poengo.set_runner_details(name)
        text['Tid'] = name[8]
        if text['Poster']:
            poster= list(map(int, text['Poster'].split()))
            poster.sort()
            text['Poster']=poster
        print(text)


if __name__=="__main__":
    main()
