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
    elif head == "Resultater":
        return {
            'Plass' : [0.07,'center'],
            'Navn' : [0.27, 'w'],
            'Klubb' : [0.2,'w'],
            'Klasse' : [0.1, 'center'],
            'Startid' : [0,1, 'center'],
            'Tid' : [0.1, 'center'],
            'Differanse' : [0.1, 'center']

        }

#    Kan jeg også putte inn dette i denne fila
#    Resultatservice
#    heading = ['Plass', 'Navn', 'Klubb', 'Klasse', 'Starttid', 'Tid', 'Differanse']
#    columnwidth = [0.07, 0.26, 0.20, 0.1, 0.1, 0.1, 0.1]
#    anchor = ['center', 'w', 'w', 'center', 'center', 'center', 'center']
#
#    Poengo
#    heading = ['Plass', 'Navn', 'Klubb', 'Tid', 'Poengsum', 'Postpoeng', 'Bonuspoeng', 'Tidstraff']
#    columnwidth = [0.05, 0.2, 0.18, 0.1, 0.1, 0.1, 0.1, 0.1]
#    anchor = ['center', 'w', 'w', 'center', 'center', 'center', 'center', 'center']
#
#
