#!/usr/bin/env python3


def bonus_points():
    return {
            'N':700,
            'DH 10':700,
            'DH 11-12':600,
            'DH 13-14':500,
            'D 15-16':400,
            'D 15-16K':400,
            'D 17-20':200,
            'D 21-39':100,
            'D 40':200,
            'D 50':300,
            'D 60':400,
            'D 70':450,
            'H 15-16':350,
            'H 17-20':150,
            'H 21-39':50,
            'H 40':150,
            'H 50':200,
            'H 60':350,
            'H 70':400,
            'C':300,
            'B':300,
            'Trim':300
            }

def bonus_track(): # Sprintstrekk og klatrestrekk må være med på listen her fordi det kan være forskjellige sprint og klatring
#    track_1 = [['74','73',75],['121','101',75],['116','70',150],['109','124',100],['103','70',100],['125','100',0]]
#    track_1 = [['120','123',75],['111','122',100],['70','115',100],['126','120',75],['103','70',100],['125','100',0]]
    track_1 = [['112','122',75],['116','105',100],['120','101',100],['121','113',100],['104','103',75],['115','100',0]]

    return {
            'N': track_1,
            'DH 10': track_1,
            'DH 11-12': track_1, 
            'DH 13-14': track_1,
            'D 15-16K': track_1, 
            'D 60': track_1, 
            'H 60': track_1, 
            'D 70': track_1, 
            'H 70': track_1, 
            'C': track_1, 
            'Trim': track_1, 
            'D 15-16': track_1,
            'H 15-16': track_1,
            'D 17-20': track_1,
            'H 17-20': track_1,
            'D 21-39': track_1,
            'H 21-39': track_1,
            'D 40': track_1, 
            'H 40': track_1, 
            'D 50': track_1, 
            'H 50': track_1,
            'H 60': track_1,
            'B': track_1 
        }

def courses():
    return {
            'N':'All',
            'DH 10':'All',
            'DH 11-12':'All',
            'DH 13-14':'All',
            'D 15-16':'All',
            'D 15-16K':'All',
            'D 17-20':'All',
            'D 21-39':'All',
            'D 40':'All',
            'D 50':'All',
            'D 60':'All',
            'D 70':'All',
            'H 15-16':'All',
            'H 17-20':'All',
            'H 21-39':'All',
            'H 40':'All',
            'H 50':'All',
            'H 60':'All',
            'H 70':'All',
            'C':'All',
            'B':'All',
            'Trim':'All'
    }    

def data():
    return {
            'maxtime' : 35, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            'climb_point':[200,100,50], # vinnern får dette poenget
            'sprint_point':[150,100,50], # vinnern fpr dette peonget
            'race_controls' : {'All': '72 73 74 101 103 104 105 112 107 108 109 110 111 113 114 115 116 120 121 122 100'},
            'bonus_tracks' : '112->122 116->105 120->101 121->113 104->103',
            'climb_track': ['104','103'], # sett til [] hvis ikke klatrestrekk
            'sprint_track': ['115','100'] # sett til klatrestrekk
    }
