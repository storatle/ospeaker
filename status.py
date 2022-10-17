#!/usr/bin/env python3
# -*- coding: utf-8 -*- 


from brikkesys import Database
from orace import Race
import config_brikkesys as config

db =Database('local')
race = Race(db,246)
#race.make_99_list()
race.check_disk_reason()
race.make_99_list()
#print(race)
#print(race.classes)
#print(race.courses)
