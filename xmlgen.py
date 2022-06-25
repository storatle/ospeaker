#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
from datetime import datetime

#time = datetime.now()
class xml:
    def __init__(self):
        print("Hello")

    def add_XMLNS_attributes(self, tree, xmlns_uris_dict):
        if not ET.iselement(tree):
            tree = tree.getroot()
        for prefix, uri in xmlns_uris_dict.items():
            tree.attrib['xmlns:' + prefix] = uri

    def result_list(self, race):
        print(race.race_name) 

        fmt = '%H:%M:%S'
        xmlns_uris = {'xsd':'http://www.w3.org/2001/XMLSchema',
                'xsi':'http://www.w3.org/2001/XMLSchema-instance'}

        root = ET.Element("ResultList", 
                iofVersion="3.0",
                creator="Brikkespy", 
                xmlns='http://www.orienteering.org/datastandard/3.0',
                createTime="2015-05-04T11:21:33.5287906", 
                status="Complete")

        self.add_XMLNS_attributes(root, xmlns_uris)
        event = ET.SubElement(root, "Event")
        ET.SubElement(event, "Name").text = race.race_name 
        startTime= ET.SubElement(event, "StartTime")
        ET.SubElement(startTime, "Date").text = "Date"
        ET.SubElement(startTime, "Time").text = "Time"
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
            print(results)
            rclass = ET.SubElement(classresult, "Class")
#        ET.SubElement(rclass, "ID").text = "1"
            ET.SubElement(rclass, "Name").text = race_class[1] 
            
#        course= ET.SubElement(classresult, "Course", raceNumber="1")
#        ET.SubElement(course, "Length").text = "4650"
#        ET.SubElement(course, "climb").text= "160"
        
            for runner in results:
                print(runner)
                personresult= ET.SubElement(classresult, "PersonResult")
                person = ET.SubElement(personresult, "Person")
                #ET.SubElement(person, "Id").runner.id
                name = ET.SubElement(person, "Name")
                ET.SubElement(name, "Family").text = runner.get('Navn')
                ET.SubElement(name, "Given").text = runner.get("Navn")
                organisation = ET.SubElement(personresult, "Organisation")
                ET.SubElement(organisation, "Id").text="5"
                ET.SubElement(organisation, "Name").text= runner.get("Klubb")
                #ET.SubElement(organisation, "Country", code="GBR").text= "Great Britain"
                result = ET.SubElement(personresult, "Result")
                #ET.SubElement(result, "BibNumber").text="101"
                ET.SubElement(result, "StartTime").text = runner.get("Starttid")
                ET.SubElement(result, "FinishTime").text ='' if runner.get("Innkomst") == None else runner.get("Innkomst").strftime(fmt)
                ET.SubElement(result, "Time").text = runner.get("Tid")
                ET.SubElement(result, "TimeBehind").text = runner.get("Differanse")
                ET.SubElement(result, "Position").text= runner.get("Plass")
                ET.SubElement(result, "Status").text="OK"

#        overall = ET.SubElement(result, "OverallResult")
#        ET.SubElement(overall, "Time").text="2001"
#        ET.SubElement(overall, "TimeBehind").text="0"
#        ET.SubElement(overall, "Position").text="1"
#        ET.SubElement(overall, "Status").text="ok"
                #controls = runner.Poster.split()

#                times = runner.Times.split(",")
#                print(times)
#                for control in runner.Poster:
#                    split =  ET.SubElement(result, "SplitTime")
#                    ET.SubElement(split, "ControlCode").control.Poster.split()
#                    ET.SubElement(split, "Time").text="501"

        tree = ET.ElementTree(root)
        tree.write("result.xml")

##
