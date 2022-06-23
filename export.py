#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
from datetime import datetime

#time = datetime.now()

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



tree = ET.ElementTree(root)
tree.write("filename.xml")
