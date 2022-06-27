#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
from datetime import datetime
from orace import Race

#time = datetime.now()
class xml:
    def __init__(self):
        print("Hello")

    def add_XMLNS_attributes(self, tree, xmlns_uris_dict):
        if not ET.iselement(tree):
            tree = tree.getroot()
        for prefix, uri in xmlns_uris_dict.items():
            tree.attrib['xmlns:' + prefix] = uri

    def result_list(self, db, race_number):
        race = Race(db, race_number)

        fmt = '%H:%M:%S'
        xmlns_uris = {'xsd':'http://www.w3.org/2001/XMLSchema',
                'xsi':'http://www.w3.org/2001/XMLSchema-instance'}

        root = ET.Element("ResultList", 
                iofVersion="3.0",
                creator="Brikkespy", 
                xmlns='http://www.orienteering.org/datastandard/3.0',
                createTime= datetime.now().isoformat(), #"2015-05-04T11:21:33.5287906", 
                status="Complete")

        self.add_XMLNS_attributes(root, xmlns_uris)
        event = ET.SubElement(root, "Event")
        ET.SubElement(event, "Name").text = race.race_name 
        startTime= ET.SubElement(event, "StartTime")
        ET.SubElement(startTime, "Date").text = race.race_date.strftime('%Y-%m-%d')#"Date"
#        ET.SubElement(startTime, "Time").text = "Time"
#        endTime = ET.SubElement(event, "EndTime")
#        ET.SubElement(endTime, "Date").text = "Date"
#        ET.SubElement(endTime, "Time").text = "Time"
#
#        race = ET.SubElement(event, "Race")
#        ET.SubElement(race, "RaceNumber").text="1"
#        ET.SubElement(race, "Name").text = "Race runner"
#        ET.SubElement(race, "StartTime")
#        ET.SubElement(race, "EndTime")
        classresult =ET.SubElement(root, "ClassResult")
        for race_class in race.classes:
            results = race.make_result_list(race_class[1])
 #           print(results)
            rclass = ET.SubElement(classresult, "Class")
#        ET.SubElement(rclass, "ID").text = "1"
            ET.SubElement(rclass, "Name").text = race_class[1] 
            
#        course= ET.SubElement(classresult, "Course", raceNumber="1")
#        ET.SubElement(course, "Length").text = "4650"
#        ET.SubElement(course, "climb").text= "160"
        
            for runner in results:
                eventor_personid = db.read_eventor_personid(runner.get('id'))
                if eventor_personid:
                    print('Eventor person id {} '.format(eventor_personid[0][2]))
                    print('Eventor club id {}'.format(eventor_personid[0][3]))
                    eventor_club = db.read_eventor_club(eventor_personid[0][3])
                    #print(eventor_club)
                print(runner)
                personresult= ET.SubElement(classresult, "PersonResult")
                person = ET.SubElement(personresult, "Person")
                name = ET.SubElement(person, "Name")
                ET.SubElement(name, "Family").text = runner.get('Navn').split()[-1]
                ET.SubElement(name, "Given").text = runner.get("Navn").replace(' '+runner.get('Navn').split()[-1],'')
                organisation = ET.SubElement(personresult, "Organisation")
                ET.SubElement(organisation, "Name").text= runner.get("Klubb")
                #ET.SubElement(organisation, "Country", code="GBR").text= "Great Britain"
                result = ET.SubElement(personresult, "Result")
                ET.SubElement(result, "BibNumber").text= runner.get('Startnr')
                ET.SubElement(result, "StartTime").text ='' if  runner.get("Starttime") == None else runner.get('Starttime').isoformat()
                ET.SubElement(result, "FinishTime").text ='' if runner.get("Innkomst") == None else runner.get("Innkomst").isoformat() #strftime(fmt)
                ET.SubElement(result, "Time").text = runner.get("Tid")
                ET.SubElement(result, "TimeBehind").text = runner.get("Differanse")
                ET.SubElement(result, "Position").text= runner.get("Plass")
                ET.SubElement(result, "Status").text="OK"

                if eventor_personid:
                    ET.SubElement(person, "Id").text =  str(eventor_personid[0][2])
                    ET.SubElement(organisation, "Id").text = str(eventor_personid[0][3])

#        overall = ET.SubElement(result, "OverallResult")
#        ET.SubElement(overall, "Time").text="2001"
#        ET.SubElement(overall, "TimeBehind").text="0"
#        ET.SubElement(overall, "Position").text="1"
#        ET.SubElement(overall, "Status").text="ok"
                #controls = runner.Poster.split()

                times = '' if runner.get('Times') == None else runner.get('Times').split(',')
                print(times)
                for control in times:
                    if control.split()[0] != '99':
                        split =  ET.SubElement(result, "SplitTime")
                        ET.SubElement(split, "ControlCode").text = control.split()[0]
                        ET.SubElement(split, "Time").text = control.split()[1]


        tree = ET.ElementTree(root)
        tree.write("result.xml")

##
