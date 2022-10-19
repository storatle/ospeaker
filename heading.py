#!/usr/bin/env python

def get_heading(head):
    "Få riktih heading til utskrift"

    # Heading for startliste for start. Inkluderer OK
    if head == 'pdf forstart':
        return {
            'OK': 0,
            'Startnr': 20,
            'Brikkenr': 60,
            'Navn': 120,
            'Klubb': 300,
            'Klasse': 430,
            'Starttid': 480
        }

    # Startlister
    elif head == 'pdf start':
        return {
            'Startnr': 20,
            'Brikkenr': 60,
            'Navn': 120,
            'Klubb': 300,
            'Klasse': 400,
            'Starttid': 480
        }

    # Resultater uten poeng
    elif head == 'pdf result':
        return {
            'Plass': 20,
            'Navn': 50,
            'Klubb': 250,
            'Tid': 380,
            'Differanse': 430
        }
    # Resultater med poeng % OG-karusell og O-6er
    elif head == 'pdf result poeng':
        return {
            'Plass': 20,
            'Navn': 50,
            'Klubb': 250,
            'Tid': 380,
            'Differanse': 430,
            'Poeng': 500
        }
    elif head == "resultater":
        return {
            'Plass': [0.07, 'center'],
            'Navn': [0.26, 'w'],
            'Klubb': [0.2, 'w'],
            'Klasse': [0.1, 'center'],
            'Starttid': [0.1, 'center'],
            'Tid': [0.1, 'center'],
            'Differanse': [0.1, 'center']

        }
    elif head == "poengo":
        return {
            'Plass': [0.05, 'center'],
            'Navn': [0.2, 'w'],
            #'Klubb': [0.18, 'w'],
            'Tid': [0.08, 'center'],
            'Sprint': [0.08,'center'],
            'Klatrestrekk': [0.08,'center'],
            'Postpoeng': [0.07, 'center'],
            'Strekkpoeng': [0.07, 'center'],
        #    'Vaksinepoeng': [0.08, 'center'],
            'Bonuspoeng': [0.07, 'center'],
            'Ekstrapoeng': [0.07, 'center'],
            'Tidstraff': [0.07, 'center'],
            'Poengsum': [0.07, 'center']
        }
# Bør denne også legges i heading.py?
def line_shift():
    return {
        'Startnr': str(''),
        'Plass': str(''),
        'Navn': str(''),
        'Klubb': str(''),
        'Tid': str(''),
        'Differanse': str(''),
        'Klasse': str(''),
        'Starttid': str(''),
        'tag': str(''),
        'Brikkenr': str(''),
        'Poeng': str('')
    }

# Bør denne også legges i heading.py?
def class_heading(class_name):
    return {
        'Startnr': str(''),
        'Plass': str(''),
        'Navn': str('Klasse: ') + class_name,
        'Klubb': str(''),
        'Tid': str(''),
        'Differanse': str(''),
        'Klasse': str(''),
        'Starttid': str(''),
        'tag': str('title'),
        'Brikkenr': str(''),
        'Poeng': str('')
    }




