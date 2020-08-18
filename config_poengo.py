#!/usr/bin/env python3


def bonus_points():
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
            'H 40': 150,
            'H 50': 200,
            'H 60': 250,
            'H 70': 350,
            }

def bonus_track():
    return {
            'Nybegynner': [['124','103',50],['133','39',50]],
            '2 km C': [['124','103',50],['133','39',50]],
            '3 km B/A': [['124','103',50],['133','39',50]]
        }

def data():
    return {
            'maxtime' : 35, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            # Controls in format from printcodes.py
            'race_controls' : '101 103 104 105 106 107 108 109 110 111 112 113 114 115 116 120 121 122 123 124'
            } 

