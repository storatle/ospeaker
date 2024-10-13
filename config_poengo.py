#!/usr/bin/env python3


def bonus_points():
    return {
            'N':700,
            'DH 10':700,
            'DH 11-12':600,
            'DH 13-14':500,
            'D 15-16':400,
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
    track_1 = [['41','100',100],['112','111',100],['67','110',100],['114','106',100],['122','113',100]]
    track_2 = [['41','100',100],['112','111',100],['122','123',100],['103','101',100],['120','103',100]]
    return {
            'N': track_1,
            'DH 10': track_1,
            'DH 11-12': track_1, 
            'DH 13-14': track_1,
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
            'N':'PoengO',
            'DH 10':'PoengO',
            'DH 11-12':'PoengO',
            'DH 13-14':'PoengO',
            'D 15-16':'PoengO',
            'D 15-16K':'PoengO',
            'D 17-20':'PoengO',
            'D 21-39':'PoengO',
            'D 40':'PoengO',
            'D 50':'PoengO',
            'D 60':'PoengO',
            'D 70':'PoengO',
            'H 15-16':'PoengO',
            'H 17-20':'PoengO',
            'H 21-39':'PoengO',
            'H 40':'PoengO',
            'H 50':'PoengO',
            'H 60':'PoengO',
            'H 70':'PoengO',
            'C':'PoengO',
            'B':'PoengO',
            'Trim':'PoengO'
    }    

def data():
    return {
            'maxtime' : 40, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            'climb_point':[200,100,50], # vinnern får dette poenget
            'sprint_point':[100,75,50], # vinnern fpr dette peonget
            # Controls in format from printcodes.py
            'race_controls' : { 'All': '41 63 64 67 70 73 74 101 103 106 108 109 110 111 112 113 114 115 116 120 122 123 124 100',
                'PoengO': '41 63 64 67 70 73 74 101 103 106 108 109 110 111 112 113 114 115 116 120 122 123 124 100',
                'alfa':  '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100',
                'beta':  '70 73 74 101 103 108 109 110 111 113 114 115 116 120 121 122 123 124 125 126 100'},
            'bonus_tracks' :'41->100 112->111 67->110 114->106 122->113 122->123 103->101 120->103', # Denne brukses når jeg skriver ut res til csv
            'climb_track': ['112','111'], # sett til [] hvis ikke klatrestrekk
            'sprint_track': ['41','100'] # sett til klatrestrekk
    }
