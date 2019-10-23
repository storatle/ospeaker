#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

from datetime import datetime, timedelta
import time
import math

class Race:
    def __init__(self, db , num, os):
        self.runners = []
        self.classes = []
        self.class_names=[]
        self.db = db
        self.get_race(num)
        self.get_classes()
        if os == 'linux':
            self.log_file = open("/var/log/ospeaker.log", "w")
        else:
            self.log_file = open("ospeaker.log", "w")


    def get_race(self, race):
        self.race = self.db.races[race]
        self.race_id = self.race[0]
        self.race_name = self.race[1]

    def get_names(self):
        self.runners=self.db.read_names(self.race_id)

    def get_classes(self):
        self.db.read_classes(self.race_id)
        for row in self.db.classes:
            if row[6] == self.race_id:
                if row[14] == 0:
                    self.class_names.append(row[1])
                    self.classes.append(row)

    def find_runner(self, startnum):
        self.get_names() # Henter navn fra databasen slik at de er oppdatert
        for name in self.runners:
            if name[7] == int(startnum):
                return name

    def find_class_name(self, class_id):
        for row in self.classes:
            if row[0] == class_id:
                return row[1]

    # Henter klasse direkte fra databasen
    def find_class(self, class_name):
        if class_name == 'all':
            return self.db.read_names(self.race_id)
        else:
            for id in self.classes:
                if id[1] == class_name:
                    class_id = id[0]
                    return self.db.read_names_from_class(self.race_id, class_id)

    def make_point_list(self):
        maxtime = 35 # minutter
        control_point = 50
        overtime_penalty = 35
        # Controls in format froma printcodes.py
        race_controls = '101 103 104 105 106 107 108 109 110 111 112 113 114 115 116 120 121 122 123 124'
        race_controls = race_controls.split(',')
        #race_controls = [str(i) for i in race_controls]
        self.heading = ['Plass','Navn', 'Klubb','Tid', 'Poengsum','Postpoeng','Bonuspoeng','Tidsstraff']
        self.get_names()
        names = self.runners
        results = []
        heading.extend(race_controls)
        for name in names:
            sum_points = 0
            time_penalty = 0
            control_points = 0
            bonus = 0
            text = self.set_runner_details(name)
            text['Tid'] = name[8]
            text['tag'] = self.set_tag(name[10])
            if text['Tid']:
                controls= list(text['Poster'].split())
                controls = list(set(controls))
                if '250' in controls:
                    controls.remove('250')
                if '100' in controls:
                    controls.remove('100')
                text['Poster'] = controls
                # Fills in with all race control codes into text and set them to ""
                for code in race_controls:
                    if code in controls:
                        text[code] = control_point
                        control_points = control_points + control_point
                    else:
                        text[code] = str('')
                sum_points = control_points
                overtime = text['Tid']-timedelta(minutes=maxtime)
                if overtime.days == 0:
                    time_penalty= math.ceil(overtime.seconds / 60) * - overtime_penalty
                    sum_points = sum_points + time_penalty
                try:
                    bonus=self.bonus_points()[text['Klasse']]
                    sum_points = sum_points + bonus
                except Exception:
                    text['Bonus']=str('')
                text['Poengsum'] = sum_points
                text['Bonuspoeng']= bonus
                text['Tidsstraff'] = time_penalty
                text['Postpoeng'] = control_points
                text['Tid'] = str(text['Tid'])
                result = []
                for title in heading:
                    result.append(text[title])
                results.append(result)
        results = sorted(results, key=lambda tup: (tup[4]) , reverse=True)
        plass=1
        for result in results:
            result[0]=plass
            plass +=1
        return results


    def make_start_list(self, class_name):
        start_list = []
        data = self.find_class(class_name)
        if data:
            data = sorted(data, key=lambda tup: str(tup[14]))  # , reverse=True)
            for name in data:
                name = list(name)
                text = { # Det kan hende at det blir tull når name[6] eller andre er tomme
                        'Startnr': str(name[7]),
                        'Plass':str(''),
                        'Navn': name[2],
                        'Klubb': name[3],
                        'Tid': (name[8]),
                        'Differanse':str(''),
                        'Klasse':self.find_class_name(name[4]),
                        'Starttid':str(''),
                        'tag':name[10],
                        'Brikkenr':str(name[6])
                        }
                # Disse under brukes kun hvis det blir krøll over
                if name[14]: #Sjekker at løper har startid
                    text['Starttid']= str(name[14].strftime('%H:%M'))
                if not text['Startnr']:
                    text['Startnr'] = ' '
                if not text['Brikkenr']:
                    text['Brikkenr'] = ' '
                if not text['Starttid']:
                    text['Starttid'] = ''
                start_list.append(text)

        return start_list

    def make_result_list(self, class_name, *args):
        urangert = False
        uten_tid = False
        results = []
        vinnertid = None
        result_list = []
        ute = []
        dns = []
        dsq = []
        arr = []
        plass = 0
        # Henter inn alle navn i klassen
        data = self.find_class(class_name)
        for name in data:
            name = list(name)
            #Setter tag
            name[10] = self.set_tag(name[10])
            # sjekker om løperen ikke er kommet i mål.
            if not name[8] or name[10] =='ute':
                #Regner ut tiden som skal vises i Vindu. Ikke på resultatlister
                name[8] = self.get_time(name[14])
            results.append(name)

        # Disse klassene bør sette i en egen config_fil
        # Her må jeg ha et flagg som sier at klasser ikke skal sortere lista
        # H 10 og D 10 skal ha urangerte lister, men det kan være med tider
        # N-åpen skal ikke ha tider bare ha fullført 
        # H/D 11-12N kan ha rangerte lister
        if (class_name == 'H -10' or class_name == 'D -10' or class_name == 'NY'): 
            # Hva gjør dette flagget?
            self.print_results = False
            urangert = True
        elif class_name == 'N-åpen':
            uten_tid = True
        else:
            #Sorterer listen
            results = sorted(results, key=lambda tup: str(tup[8]))  # , reverse=True)

        # regne ut differanse i forhold til ledertid
        # Finn vinnertiden
        for name in results:
            text = self.set_runner_details(name)
            # Sjekker om løperen ikke er disket eller ikke har startet eller er arrangør
            # Endrer til å sjekke om løperen er inne:
            # if not (name[10] == 'dsq' or name[10] == 'dns' or name[10] == 'arr' or name[10] == 'ute'):
            # Sjekker om løper har kommet i mål
            # if text['tag'] == 'inne':
                # Det er mulig denne kan droppes hvis det leses direkte inn hvis tiden er tom
            if name[14]: #Sjekker at løper har startid
                text['Starttid'] = str(name[14].time())
            if uten_tid:
                text['Tid'] = str('fullført')
            if text['tag'] == 'ute':
                ute.append(text)
            if text['tag'] == 'dsq':
                text['Tid'] = str('DSQ')
                dsq.append(text)
                continue
            if text['tag'] == 'dns':
                text['Tid'] = str('DNS')
                dns.append(text)
                continue
            if text['tag'] == 'arr':
                text['Tid'] = str('Arrangør')
                arr.append(text)
                continue
            if not vinnertid:
                # Setter vinnertiden til øverste på lista siden den er sortert
                vinnertid = name[8]
            if urangert or uten_tid:
                result_list.append(text)
            else:
                plass += 1
                text['Plass'] = str(plass)
                # Finner differansen til vinner tid
                try:
                    diff = name[8] - vinnertid
                    text['Differanse'] = str(diff)
                    
                    # regner ut poeng for løperen
                    text['Poeng'] = int(round(100 - 50 * (name[8]-vinnertid) / vinnertid))
                    if text['Poeng'] <= 50:
                        text['Poeng'] = str(50)
                    else:
                        text['Poeng'] = str(text['Poeng'])
                except:
                    diff = None
                result_list.append(text)
        result_list.extend(dsq)
        result_list.extend(dns)
        result_list.extend(arr)
        liste=[x for x in result_list if x not in ute]
        # Denne returnerer lista over de som er ute hvis det er for ute
        for arg in args:
            if arg == 'out':
                return ute
        return liste

    def set_runner_details(self, name):
        text = {

                'Startnr': name[7],
                'Plass':str(''),
                'Navn': name[2],
                'Klubb': name[3],
                'Tid': str(name[8]),
                'Differanse':str(''),
                'Klasse':self.find_class_name(name[4]),
                'Starttid':str(''),
                'tag':name[10],
                'Brikkenr':str(name[6]),
                'Poeng':str(''),
                'Poster': name[17]
                 }
                 # Disse under brukes kun hvis det blir krøll over
        if name[14]: #Sjekker at løper har startid
            text['Starttid']= str(name[14].strftime('%H:%M'))
        return text
 
    def get_time(self, starttime):
        spurt = 0
        # sjekker om løperen har startet
        if starttime:
            if (datetime.now() - starttime).days >= 0:
                now = time.strftime('%H:%M:%S')
                fmt = '%H:%M:%S'
                atime = datetime.strptime(now, fmt) - timedelta(0, abs(spurt))
                tdelta = atime - starttime
                return (abs(timedelta(days=tdelta.days))+tdelta)

        return None

    def set_tag(self, tag):
        if tag == 'I':
            return 'ute'
        elif tag == 'A':
            return 'inne'
        elif tag == 'D':
            return 'dsq'
        elif tag == 'N':
            return 'dns'
        elif tag == 'X':
            return 'arr'
        elif tag == 'E': #Brutt
            return 'dns'
        elif tag == 'H': #Startet
            return 'ute'
        elif tag == 'C': #Omstart
            return 'ute'
        elif tag == 'P': #Bekreftet tid
            return 'inne'
        else:
            self.log_file.write("Cannot find tag {0}: \n".format(str(tag)))
            self.log_file.flush()

    def bonus_points(self):
        return {
            'N':500,
            'D 10':500,
            'D 11-12':400,
            'D 13-14':350,
            'D 15-16':250,
            'D 17-20':200,
            'D 21-39':150,
            'D 40':200,
            'D 50':300,
            'D 60':350,
            'D 70':400,
            'H 10': 500,
            'H 11-12': 400,
            'H 13-14': 250,
            'H 15-16': 150,
            'H 17-20': 50,
            'H 21-39': 0,
            'H 40': 150,
            'H 50': 200,
            'H 60': 250,
            'H 70': 350,
        }

