#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

from datetime import datetime, timedelta
import time

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
                        'Diff':str(''),
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
                    text['Diff'] = str(diff)
                    
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
                'Diff':str(''),
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


