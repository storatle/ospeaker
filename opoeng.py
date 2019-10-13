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
    controls = [101, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 120, 121, 122, 123, 124]
    controls = map(str, controls)
    heading = ['Navn', 'Klubb','Tid', 'Poengsum','Postpoeng','Bonuspoeng','Tidstraff']
    heading.extend(controls)
    print(heading)
    for name in names:
        poeng = 0
        tidstraff = 0
        post_poeng = 0
        bonus = 0
        text = poengo.set_runner_details(name)
        for code in controls:
            text[code] = str('')
        text['Tid'] = name[8]
        if text['Poster']:
            poster= list(text['Poster'].split())
            poster = list(set(poster))
            poster.remove('250')
            poster.remove('100')
            text['Poster'] = poster
            post_poeng = len(poster)*50
            poeng = post_poeng
            for post in poster:
                text[post]=50
            overtid = text['Tid']-timedelta(minutes=maxtid)
            if overtid.days == 0:
                tidstraff= math.ceil(overtid.seconds / 60) * -35
            poeng = poeng + tidstraff
            try:
                bonus=bonus_points()[text['Klasse']]
                poeng = poeng + bonus
            except Exception:
                text['Bonus']=str('')
        text['Poengsum']= str(poeng)
        text['Bonuspoeng']=str(bonus)
        text['Tidstraff'] =str(tidstraff)
        text['Postpoeng'] = str(post_poeng)
        print(text['Navn']+' '+text['Klubb']+' '+str(text['Tid'])+' '+text['Poengsum']+' '+text['Postpoeng']+' '+text['Bonuspoeng']+' '+text['Tidstraff']+(' '.join(str(text[x]) for x in controls))
)

if __name__=="__main__":
    main()

#with open('employee_file2.csv', mode='w') as csv_file:
#    fieldnames = ['emp_name', 'dept', 'birth_month']
#    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#
#    writer.writeheader()
#    writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
#    writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})


#import csv
#
#with open('employee_file.csv', mode='w') as employee_file:
#    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#
#    employee_writer.writerow(['John Smith', 'Accounting', 'November'])
#    employee_writer.writerow(['Erica Meyers', 'IT', 'March'])
