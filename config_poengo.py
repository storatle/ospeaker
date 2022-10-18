#!/usr/bin/env python3


def bonus_points():
    return {
            'N':700,
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
#    var track_1 = [['74','73',150],['121','101',150],['116','70',150],['73','110',150],['103','70',150],['125','100',150]]
#    var track_2 = [['120','123',150],['111','115',150],['70','115',150],['116','120',150],['103','70',150],['125','100',150]]
    track_1 = [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]]
    track_2 = [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]]
    return {
            'N': track_1, 
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

#            'N': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'DH 11-12': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'DH 13-14': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'D 60': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'H 60': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'D 70': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'H 70': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'C': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#            'Trim': [['74','73',75],['70','110',100],['123','73',100],['115','114',100],['103','70',100],['41','100',0]],
#
#            'D 15-16': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'H 15-16': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'D 17-20': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'H 17-20': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'D 21-39': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'H 21-39': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'D 40': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'H 40': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'D 50': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'H 50': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]],
#            'B': [['110','115',100],['122','124',100],['70','122',100],['103','70',100],['41','100',0]]
        }

def courses():
    return {
            'N':'alfa',
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

#def climb():
##    return {'climb': []}
#    return {'climb': ['123','133']}
##
#def sprint():
##    return {'sprint': []}
#    return {'sprint': ['110','121']}

def data():
    return {
            'maxtime' : 40, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            'climb_point':100, # vinnern får dette poenget
            'sprint_point':100, # vinnern fpr dette peonget
            # Controls in format from printcodes.py
            'race_controls' : {'All':'101 121 67 115 116 132 122 120 107 111 113 131 106 112 110 105 133 123 73 130 108 70 72 103',
                'alfa':'67 70 73 101 103 105 106 110 123 130 131',
                'beta':'67 101 105 107 108 111 112 115 122 123 131'},
            'bonus_tracks' : '70->72 101->121 110->112 111->120 115->116 122->132 123->133 130->108 131->113',
            'climb_track': ['123','133'], # sett til [] hvis ikke klatrestrekk
            'sprint_track': ['110','112'] # sett til klatrestrekk
            }

