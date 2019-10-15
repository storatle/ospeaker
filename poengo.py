#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
from orace import Race
from brikkesys import Database
from datetime import datetime, timedelta
import math
import csv

class Poengo():
    def  __init__(self,db,num,os):
        self.db = db
        self.os = os
        self.race_number = num
        self.heading = ['Plass','Navn', 'Klubb','Tid', 'Poengsum','Postpoeng','Bonuspoeng','Tidstraff']

    def bonus_points(self):
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
            'H 40': 0,
            'H 50': :50,
            'H 60': 250,
            'H: 70': 350,
        }

    def set_result_text(iself,name):
            text = {
                'Startnr': str(' '),
                'Plass': name[0],
                'Navn': name[1],
                'Klubb': name[2],
                'Tid': str(name[3]),
                'Poengsum': str(name[4]),
                'Postpoeng': str(name[5]),
                'Bonuspoeng': str(name[6]),
                'Tidstraff': str(name[7]),
                'tag':str(name[10]),
            }
            return text

    def result_list(self):
        maxtime = 35 # minutter
        control_point = 50
        overtime_penalty = 35
        #race_number = 153
        #os = 'linux'
        #db = Database('local','linux')
        poengo = Race(self.db, self.race_number, self.os)
        poengo.get_names()
        names = poengo.runners
        race_controls = [101, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 120, 121, 122, 123, 124]
        race_controls = [str(i) for i in race_controls]
        results = []
        self.heading.extend(race_controls)
        for name in names:
            sum_points = 0
            time_penalty = 0
            control_points = 0
            bonus = 0
            text = poengo.set_runner_details(name)
            text['Tid'] = name[8]
            text['tag'] = poengo.set_tag(name[10])
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
                    bonus=self.bonus_points()[text['Klasse']]
                    sum_points = sum_points + bonus
                except Exception:
                    text['Bonus']=str('')
                text['Poengsum'] = (sum_points)
                text['Bonuspoeng']= (bonus)
                text['Tidstraff'] = (time_penalty)
                text['Postpoeng'] = (control_points)
                text['Tid'] = str(text['Tid'])
                result = []
                for title in self.heading:
                    result.append(text[title])
                results.append(result)
        results = sorted(results, key=lambda tup: (tup[3]))# , reverse=True)
        plass=1
        for result in results:
            result[0]=plass
            plass +=1
        return results

    def write_results(self, results):
        result_writer = csv.writer(open("resultater.csv", "w"))
        results.insert(0, self.heading)
        result_writer.writerows(results)

    def make_treeview_list(self, results):
        tree_results=[]
        for result in results:
            tree_results.append(self.set_result_text(result))
        return tree_results       
