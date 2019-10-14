#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
from orace import Race
from brikkesys import Database
from datetime import datetime, timedelta
import math
import csv

def bonus_points():
    #Få riktid heading til utskrift

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
        '3 km B/A': 1000
    }

def main():
    maxtime = 35 # minutter
    control_point = 50
    overtime_penalty = 35
    race_number = 153
    os = 'linux'
    db = Database('local','linux')
    poengo = Race(db, race_number, os)
    poengo.get_names()
    names = poengo.runners
    race_controls = [101, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 120, 121, 122, 123, 124]
    race_controls = [str(i) for i in race_controls]
    results = []
    heading = ['Navn', 'Klubb','Tid', 'Poengsum','Postpoeng','Bonuspoeng','Tidstraff']
    heading.extend(race_controls)
    result_writer = csv.writer(open("resultater.csv", "w"))
    for name in names:
        sum_points = 0
        time_penalty = 0
        control_points = 0
        bonus = 0
        text = poengo.set_runner_details(name)
        text['Tid'] = name[8]
        # checks it the runner has any controls. Should I also check the time?
        if text['Tid']:
            controls= list(text['Poster'].split())
            controls = list(set(controls))
            controls.remove('250')
            controls.remove('100')
            text['Poster'] = controls
             # Fills in with all race control codes into text and set them to ""
            for code in race_controls:
                if code in controls:
                    text[code] = control_point
                    control_points = control_points + control_point
                else:
                    text[code] = str('')
            sum_points = control_points
            overtime = text['Tid']-timedelta(minutes=maxtime)
            if overtime.days == 0:
                time_penalty= math.ceil(overtime.seconds / 60) * - overtime_penalty
                sum_points = sum_points + time_penalty
            try:
                bonus=bonus_points()[text['Klasse']]
                sum_points = sum_points + bonus
            except Exception:
                text['Bonus']=str('')
            text['Poengsum'] = (sum_points)
            text['Bonuspoeng']= (bonus)
            text['Tidstraff'] = (time_penalty)
            text['Postpoeng'] = (control_points)
            text['Tid'] = str(text['Tid'])
            result = []
            #print(text['Navn']+' '+text['Klubb']+' '+str(text['Tid'])+' '+text['Poengsum']+' '+text['Postpoeng']+' '+text['Bonuspoeng']+' '+text['Tidstraff']+(' '.join(str(text[x]) for x in race_controls)))
            for title in heading:
                result.append(text[title])
            results.append(result)
    results = sorted(results, key=lambda tup: (tup[3]) , reverse=True)
    results.insert(0, heading)
    result_writer.writerows(results)

if __name__=="__main__":
    main()

