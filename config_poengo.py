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
    track_1 = [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',100]]
    track_2 = [['110','115',100],['122','124',100],['70','122',750],['103','70',100],['41','100',100]]
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
            'maxtime' : 40, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            'climb_point':[200,100,50], # vinnern får dette poenget
            'sprint_point':[200,100,50], # vinnern fpr dette peonget
            # Controls in format from printcodes.py
            'race_controls' : {'All': '41 70 73 74 101 103 106 108 109 110 111 112 113 114 115 116 120 121 122 123 124 100',
                'alfa':  '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100',
                'beta':  '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100'},
            'bonus_tracks' :'74->73 70->110 123->73 115->114 110-115 122->124 70->122 103->70 41->100', # Denne brukses når jeg skriver ut res til csv
            'climb_track': ['103','70'], # sett til [] hvis ikke klatrestrekk
            'sprint_track': ['41','100'] # sett til klatrestrekk
    }
