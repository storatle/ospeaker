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
    track_1 = [['74','73',75],['121','101',75],['116','70',150],['109','124',100],['103','70',100],['125','100',0]]
    track_2 = [['120','123',75],['111','122',100],['70','115',100],['126','120',75],['103','70',100],['125','100',0]]
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

            'D 15-16': track_2,
            'H 15-16': track_2,
            'D 17-20': track_2,
            'H 17-20': track_2,
            'D 21-39': track_2,
            'H 21-39': track_2,
            'D 40': track_2, 
            'H 40': track_2, 
            'D 50': track_2, 
            'H 50': track_2,
            'H 60': track_2,
            'B': track_2 
        }

def courses():
    return {
            'N':'alfa',
            'DH 10':'alfa',
            'DH 11-12':'alfa',
            'DH 13-14':'alfa',
            'D 15-16':'beta',
            'D 15-16K':'alfa',
            'D 17-20':'beta',
            'D 21-39':'beta',
            'D 40':'beta',
            'D 50':'beta',
            'D 60':'alfa',
            'D 70':'alfa',
            'H 15-16':'beta',
            'H 17-20':'beta',
            'H 21-39':'beta',
            'H 40':'beta',
            'H 50':'beta',
            'H 60':'beta',
            'H 70':'alfa',
            'C':'alfa',
            'B':'beta',
            'Trim':'alfa'
    }    

def data():
    return {
            'maxtime' : 40, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            'climb_point':[200,100,50], # vinnern får dette poenget
            'sprint_point':[150,100,50], # vinnern fpr dette peonget
            # Controls in format from printcodes.py
            'race_controls' : {'All': '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100',
                'alfa':  '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100',
                'beta':  '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100'},
            'bonus_tracks' : '74->73 109-124 121->101 116->70 120->123 111->122 70->115 126->120',
            'climb_track': ['103','70'], # sett til [] hvis ikke klatrestrekk
            'sprint_track': ['125','100'] # sett til klatrestrekk
    }
