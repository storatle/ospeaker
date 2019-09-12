#!/usr/bin/env python3
# -*- coding: utf-8 -*- 


def result_list(self, race, class_name, page_break):
    self.class_name = class_name
    self.race_name = race.race_name
    race_classes = race.classes
    for race_class in race_classes:
        # Henter resultatliste for klassen
        result_list = race.make_result_list(race_class[1])
        if result_list: # Sjekker om det er deltaker i klassen
            self.active_class = race_class[1]
            self.make_list(result_list, head, 'result.pdf') # Filnavn bør være en variabel
            calc_points()


def calc_points(results):
    # Bør jeg bare flytte denne inn i ospeaker?
    # Og så kan jeg lage en egen utskriftsmodul for poengberegninger i pdfgen.py
    # Finner tid til første løper og setter den som vinnertid
    vinnertid = results[0]['Tid'] # Er denne string nå? Den må endres til vanlig tid
    for runner in results:
        runner['Poeng'] = 100 * 50 * (runner['Tid']-vinnertid) / vinnertid
        if runner['Poeng'] =< 50:
            runner['Poeng'] = 50
   
    

def set_runner_details(self, name):
    text = {

            'Startnr': name[7],
            'Plass':str(''),
            'Navn': name[2],
            'Klubb': name[3],
            'Tid': str(name[8]),
            'Diff':str(''),
            'Klasse':self.find_class_name(name[4]),
            'Starttid':str(''),
            'tag':name[10],
            'Brikkenr':str(name[6])
             }
             # Disse under brukes kun hvis det blir krøll over
    if name[14]: #Sjekker at løper har startid
        text['Starttid']= str(name[14].strftime('%H:%M'))
    return text
    

