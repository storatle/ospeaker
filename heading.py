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
            'Klubb':250,
            'Klasse':340,
            'Starttid':450

        }

    elif head ==2:
        return {

            'Startnr': 20,
            'Brikkenr': 60,
            'Navn': 120,
            'Klubb': 350,
            'Klasse': 430,
            'Starttid': 480

        }
 
    elif head ==3:
        return {

            'Plass': 20,
            'Navn': 120,
            'Klubb': 350,
            'Tid': 430,
            'Diff': 480

        }
               
