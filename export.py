#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
from datetime import datetime

#time = datetime.now()
class xml:
    def __init__(self):
        root = ET.Element("ResultList", iofVersion="3.0",creator="Brikkespy")
        event = ET.SubElement(root, "Event")

        ET.SubElement(event, "Name").text = "Event name"
        startTime= ET.SubElement(event, "StartTime")
        ET.SubElement(startTime, "Date").text = "Date"
        ET.SubElement(startTime, "Time").text = "Time"
        endTime = ET.SubElement(event, "EndTime")
        ET.SubElement(endTime, "Date").text = "Date"
        ET.SubElement(endTime, "Time").text = "Time"

        race = ET.SubElement(event, "Race")
        ET.SubElement(race, "RaceNumber").text="1"
        ET.SubElement(race, "Name").text = "Race name"
        ET.SubElement(race, "StartTime")
        ET.SubElement(race, "EndTime")

        classresult =ET.SubElement(root, "ClassResult")
        rclass = ET.SubElement(classresult, "Class")
        ET.SubElement(rclass, "ID").text = "1"
        ET.SubElement(rclass, "Name").text = "Course name"
            
        course= ET.SubElement(classresult, "Course", raceNumber="1")
        ET.SubElement(course, "Length").text = "4650"
        ET.SubElement(course, "climb").text= "160"

        personresult= ET.SubElement(classresult, "PersonResult")

        person = ET.SubElement(personresult, "Person")

        ET.SubElement(person, "Id").text="1"
        name = ET.SubElement(person, "Name")
        ET.SubElement(name, "Family").text="Wood"
        ET.SubElement(name, "Given").text="George"

        organisation = ET.SubElement(personresult, "Organisation")
        ET.SubElement(organisation, "Id").text="5"
        ET.SubElement(organisation, "Name").text= "OC Back and Forth"
        ET.SubElement(organisation, "Country", code="GBR").text= "Great Britain"

        result = ET.SubElement(personresult, "Result", raceNumber="1")
        ET.SubElement(result, "BibNumber").text="101"
        ET.SubElement(result, "StartTime").text="Start time"
        ET.SubElement(result, "FinishTime").text="Finish time"
        ET.SubElement(result, "Time").text="2001"
        ET.SubElement(result, "TimeBehind").text="0"
        ET.SubElement(result, "Position").text="1"
        ET.SubElement(result, "Status").text="ok"
        overall = ET.SubElement(result, "OverallResult")
        ET.SubElement(overall, "Time").text="2001"
        ET.SubElement(overall, "TimeBehind").text="0"
        ET.SubElement(overall, "Position").text="1"
        ET.SubElement(overall, "Status").text="ok"

        split =  ET.SubElement(result, "SplitTime")
        ET.SubElement(split, "ControlCode").text="31"
        ET.SubElement(split, "Time").text="501"

        tree = ET.ElementTree(root)
        tree.write("result.xml")

##
