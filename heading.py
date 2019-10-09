#!/usr/bin/env python

def get_heading(head):
    "Få riktih heading til utskrift"

    # Heading for startliste for start. Inkluderer OK
    if head == 1:
        return {
            'OK':0,
            'Startnr':20,
            'Brikkenr':60,
            'Navn':120,
            'Klubb':300,
            'Klasse':430,
            'Starttid':480
        }

# Startlister
    elif head ==2:
        return {
            'Startnr': 20,
            'Brikkenr': 60,
            'Navn': 120,
            'Klubb': 300,
            'Klasse': 430,
            'Starttid': 480
        }
 
 # Resultater uten poeng       
    elif head ==3:
        return {
            'Plass': 20,
            'Navn': 50,
            'Klubb': 250,
            'Tid': 380,
            'Diff': 430
        }
 # Resultater med poeng % OG-karusell og O-6er 
    elif head ==4:
        return {
            'Plass': 20,
            'Navn': 50,
            'Klubb': 250,
            'Tid': 380,
            'Diff': 430,
            'Poeng': 500
        }
              
