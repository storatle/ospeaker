#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
from datetime import datetime,timedelta
from orace import Race
import decimal as dec

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
        
        invoice_level = db.read_invoicelevel(race_number)

        fmt = '%H:%M:%S'
        xmlns_uris = {'xsd':'http://www.w3.org/2001/XMLSchema',
                'xsi':'http://www.w3.org/2001/XMLSchema-instance'}

        root = ET.Element("ResultList", 
                iofVersion="3.0",
                xmlns='http://www.orienteering.org/datastandard/3.0',
                createTime= datetime.now().isoformat(), #"2015-05-04T11:21:33.5287906", 
                creator="Brikkespy", 
                status="Complete")

        self.add_XMLNS_attributes(root, xmlns_uris)
        event = ET.SubElement(root, "Event")
        ET.SubElement(event, "Name").text = race.race_name 
        startTime= ET.SubElement(event, "StartTime")
        ET.SubElement(startTime, "Date").text = race.race_date.strftime('%Y-%m-%d')#"Date"
        endTime= ET.SubElement(event, "StartTime")
        ET.SubElement(endTime, "Date").text = race.race_date.strftime('%Y-%m-%d')#"Date"
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
                print("runner name: {}".format(runner.get("Navn")))
                print("runner.get(Tid) {} ".format(runner.get("Tid")))
                eventor_personid = db.read_eventor_personid(runner.get('id'))
                if eventor_personid:
                    print('Eventor person id {} '.format(eventor_personid[0][2]))
                    print('Eventor club id {}'.format(eventor_personid[0][3]))
                    eventor_club = db.read_eventor_club(eventor_personid[0][3])
                    #print(eventor_club)
            #    print(runner)
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
                try:
                    date_time = datetime.strptime(runner.get("Tid"), "%H:%M:%S")
                    a_timedelta = date_time - datetime(1900, 1, 1)
                    ET.SubElement(result, "Time").text = str(int(a_timedelta.total_seconds()))#.seconds()
                except:
                    ET.SubElement(result, "Time").text = str(runner.get("Tid"))#.seconds()
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
                print(times[0:-2])
                for control in times[0:-2]:
                    if control.split()[0] != '99':
                        split =  ET.SubElement(result, "SplitTime")
                        ET.SubElement(split, "ControlCode").text = control.split()[0]
                        ET.SubElement(split, "Time").text = control.split()[1]
                
                if invoice_level:

                    print("Amount {}".format(invoice_level[1][5]))

                    print("Innvoice: {}".format(runner.get("Invoice")))
                    try:
                        ind = [el.index(runner.get("Invoice")) for i, el in enumerate(invoice_level) if runner.get("Invoice") in el][0]
                        person_level = invoice_level[[el.index(runner.get("Invoice")) for i, el in enumerate(invoice_level) if runner.get("Invoice") in el][0]]
                        print([(i, el.index(runner.get("Invoice"))) for i, el in enumerate(invoice_level) if runner.get("Invoice") in el])
                        assignedfee = ET.SubElement(result, "AssignedFee")
                        fee = ET.SubElement(assignedfee, "Fee")
                        ET.SubElement(fee, "Name").text = person_level[3]
                        print("Amount2 {}".format(person_level[5]))
                        ET.SubElement(fee, "Amount").text = str(person_level[5])

                    except:
                        print('Invoice level id {} '.format(invoice_level[0][2]))
                    
                print('Invoice level id {} '.format(invoice_level))
        tree = ET.ElementTree(root)
        tree.write("result.xml")

##
