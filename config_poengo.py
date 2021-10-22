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
            'H 15-16': 350,
            'H 17-20': 150,
            'H 21-39': 50,
            'H 40': 150,
            'H 50': 200,
            'H 60': 350,
            'H 70': 400,
            'C':200,
            'B':300,
            'Trim':'400'
            }

def bonus_track(): # Sprintstrekk og klatrestrekk må være med på listen her fordi det kan være forskjellige sprint og klatring
    return {
            'N': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'DH 11-12': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'DH 13-14': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'D 15-16K': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'D 60': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'H 60': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'D 70': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'H 70': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'C': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],
            'Trim': [['130','108',150],['123','133',150],['110','112',150],['131','113',150],['70','72',150],['101','121',150]],

            'D 15-16': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'H 15-16': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'D 17-20': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'H 17-20': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'D 21-39': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'H 21-39': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'D 40': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'H 40': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'D 50': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'H 50': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'H 60': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]],
            'B': [['123','133',150],['131','113',150],['111','120',150],['122','132',150],['115','116',150],['101','121',150]] 

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
#    return {'climb': []}
##    return {'climb': ['103','70']}
#
#def sprint():
#    return {'sprint': []}
##    return {'sprint': ['41','100']}

def data():
    return {
            'maxtime' : 40, # minutter
            'control_point' : 50,
            'overtime_penalty' : 35,
            # Controls in format from printcodes.py
            'race_controls' : {'All':'101 121 67 115 116 132 122 120 107 111 113 131 106 112 110 105 133 123 73 130 108 70 72 103',
                'alfa':'67 70 73 101 103 105 106 110 123 130 131',
                'beta':'67 101 105 107 108 111 112 115 122 123 131'},
            #'race_controls' : '41 70 73 74 101 103 108 109 110 111 112 113 114 115 116 120 121 122 123 124 100',
            'bonus_tracks' : '70->72 101->121 110->112 111->120 115->116 122->132 123->133 130->108 131->113',
           # 'bonus_tracks' : '74->73 70->110 123->73 115->114 110->115 122->124 70->122',
            'climb_track': [], # ['103','0'],
            'sprint_track':[] # ['103','100']
            }

