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


def calc_points():


