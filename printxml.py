#!/usr/bin/env python3
# -*- coding: utf-8 -*- 


from brikkesys import Database
import xmlgen
import heading as hdn
from orace import Race

def main():
    race_number = 244
    db = Database('local')
    xml_list(db, race_number)
    #race = Race(db, race_number)

def xml_list(db, race_number):
    xml = xmlgen.xml()
    #race = Race(self.db, race_number)
    xml.result_list(db, race_number)



if __name__=="__main__":
    main()  # Create GUI
 
