#!/usr/bin/env python

def get_heading(head):
    "Få riktih heading til utskrift"

    # Heading for startliste for start. Inkluderer OK
    if head == 1:
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
    elif head == 2:
        return {
            'Startnr': 20,
            'Brikkenr': 60,
            'Navn': 120,
            'Klubb': 300,
            'Klasse': 430,
            'Starttid': 480
        }

    # Resultater uten poeng
    elif head == 3:
        return {
            'Plass': 20,
            'Navn': 50,
            'Klubb': 250,
            'Tid': 380,
            'Differanse': 430
        }
    # Resultater med poeng % OG-karusell og O-6er
    elif head == 4:
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
            'Klubb': [0.18, 'w'],
            'Tid': [0.1, 'center'],
            'Poengsum': [0.1, 'center'],
            'Postpoeng': [0.1, 'center'],
            'Bonuspoeng': [0.1, 'center'],
            'Tidstraff': [0.1, 'center']
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




