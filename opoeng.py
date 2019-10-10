#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
from orace import Race
from brikkesys import Database
from datetime import datetime, timedelta
import math
def bonus_points():
    "Få riktih heading til utskrift"

    return {
        'N':500,
        'D 10':500,
        'D 11-12':400,
        'D 13-14':350,
        'D 15-16':250,
        'D 17-20':200,
        'D 21-39':150,
        'D 40':200,
        'D 50':300,
        'D 60':350,
        'D 70':400,
        'H 10': 500,
        'H 11-12': 400,
        'H 13-14': 250,
        'H 15-16': 150,
        'H 17-20': 50,
        'H 21-39': 0,
        'H 40': 100,
        'H 50': 150,
        'H 60': 250,
        'H: 70': 350,
        '3 km B/A': 500

    }


def main():
    maxtid = 35 # minutter
    race_number = 151
    os = 'linux'
    db = Database('local','linux')
    poengo = Race(db, race_number, os)
    poengo.get_names()
    names = poengo.runners
    check_points = ['39', '113', '38', '106', '124', '133', '114', '37', '105', '103','31','35','45','56']
    for name in names:
        poeng = 0
        tidstraff = 0
        post_poeng = 0
        bonus = 0
        text = poengo.set_runner_details(name)
        for code in check_points:
            text[code] = str('')
        text['Tid'] = name[8]
        if text['Poster']:
            poster= list(text['Poster'].split())
            poster = list(set(poster))
            poster.remove('250')
            poster.remove('100')
            #poster.sort()
            text['Poster'] = poster
            post_poeng = len(poster)*50
            poeng = post_poeng
            for post in poster:
                text[post]=50
            overtid = text['Tid']-timedelta(minutes=maxtid)
            if overtid.days == 0:
                tidstraff= math.ceil(overtid.seconds / 60) * 35
            poeng = poeng - tidstraff

        try:
            bonus=bonus_points()[text['Klasse']]
            poeng = poeng + bonus
        except Exception:
            text['Bonus']=str('')

        text['Sum poeng']= str(poeng)
        text['Bonus']=str(bonus)
        text['Tidstraff'] =str(tidstraff)
        text['Poeng'] = str(post_poeng)
        text['Post poeng'] = str(post_poeng)

        print(text['Navn']+' '+text['Klubb']+' '+text['Sum poeng']+' '+text['Post poeng']+' '+str(text['Tid'])+' '+text['Bonus']+' '+text['Tidstraff'])

if __name__=="__main__":
    main()
