#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

from datetime import datetime, timedelta
import time
import math
import config_poengo as poengo

class Race:
    def __init__(self, db , num, os):
        self.runners = []
        self.classes = []
        self.class_names=[]
        self.db = db
        self.idx = 0
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

                text = self.set_runner_details(name)
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

        # Disse klassene bør sette i en egen config_fil Eller kan det hentes direkte fra brikkesys?
        # Her må jeg ha et flagg som sier at klasser ikke skal sortere lista
        # H 10 og D 10 skal ha urangerte lister, men det kan være med tider
        # N-åpen skal ikke ha tider bare ha fullført 
        # H/D 11-12N kan ha rangerte lister
        if (class_name == 'H -10' or class_name == 'D -10' or class_name == 'NY'): 
            # Hva gjør dette flagget?
            self.print_results = False
            urangert = True
        # N-åpen skal ikke ha tid, bare fullført    
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
            # Sjekker om løper har kommet i mål
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

    def make_prewarn_list(self, pre_db):
        prewarn_list = []
        prewarn_runners = self.get_prewarn_runners(pre_db)
        for runner in prewarn_runners:
            runner = list(runner)
            runner[10] = self.set_tag(runner[10])
            # sjekker om løperen ikke er kommet i mål.
            if runner[10] == 'ute':
                # Regner ut tiden som skal vises i Vindu. Ikke på resultatlister
                try:
                    runner[8] = self.get_time(runner[14])
                except:
                    if runner[10] == 'dns':
                        runner[8] = 'DNS'
            if not runner[8]:
                runner[8] = runner[10]
            prewarn_list.insert(0, self.set_runner_details(runner))
        return prewarn_list

    #Henter løpere fra forvarseldatabasen. Skal denne vare i orace.py?
    def get_prewarn_runners(self, pre_db):
        # Henter startnummer fra prewarningsdatabasen
        nums = pre_db.read_start_numbers()
        runners = []
        for num in nums:
            if self.idx < num[0]:
                self.idx = num[0]
                try:
                    start_num = int(num[1])
                    runner = self.find_runner(start_num)
                    if runner:
                        runners.append(runner)
                except:
                    str_num = num
                    self.log_file.write("No startnumbers {0}: \n".format(str(num)))
                    self.log_file.flush()
        return runners

    # lager liste over PoengO
    def make_point_list(self):
        data = poengo.data
        maxtime = poengo.data()['maxtime']
        overtime_penalty = poengo.data()['overtime_penalty']
        control_point = poengo.data()['control_point']
        race_controls = poengo.data()['race_controls']
        race_controls = race_controls.split()
        bonus_tracks = poengo.data()['bonus_tracks']
        bonus_tracks = bonus_tracks.split()
        #race_controls = [str(i) for i in race_controls]
        self.heading = ['Plass','Navn', 'Klubb','Tid', 'Poengsum','Postpoeng','Strekkpoeng','Bonuspoeng','Tidsstraff']
        self.get_names()
        names = self.runners
        results = []
        self.heading.extend(race_controls)
        self.heading.extend(bonus_tracks)
        for name in names:
            sum_points = 0
            time_penalty = 0
            control_points = 0
            track_points = 0
            bonus = 0
            text = self.set_runner_details(name)
            text['Tid'] = name[8]
            text['tag'] = self.set_tag(name[10])
            if text['Tid']:
                controls= list(text['Poster'].split())
                #print(controls)
                #controls = list(set(controls))
                #print(controls)
                controls = [x for x in controls if x != '99']
                controls = [x for x in controls if x != '250']
                controls = [x for x in controls if x != '100']
                text['Poster'] = controls
                # print(controls)
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
                    bonus=poengo.bonus_points()[text['Klasse']]
                    sum_points = sum_points + bonus
                except Exception:
                    text['Bonus']=str('')
                try: # Hente inn bonus  tracks
                    tracks = poengo.bonus_track()[text['Klasse']]
                    for track in bonus_tracks:
                        text[track] = str('')
                    for track in tracks:
                        if (track[0] in controls) and (track[1] in controls):
                            ind = controls.index(track[1]) - controls.index(track[0])
                            if ind == 1:
                                track_points = track_points + track[2]
                                text[track[0] + "->" + track[1]] = track[2]
                        sum_points = sum_points + track_points
                except Exception:
                    text['Strekkpoeng']=str('')

                text['Poengsum'] = sum_points
                text['Bonuspoeng']= bonus
                text['Tidsstraff'] = time_penalty
                text['Postpoeng'] = control_points
                text['Strekkpoeng'] = track_points
                text['Tid'] = str(text['Tid'])
                result = []
                for title in self.heading:
                    result.append(text[title])
                results.append(result)
        results = sorted(results, key=lambda tup: (tup[4]) , reverse=True)
        plass=1
        for result in results:
            result[0]=plass
            plass +=1
        return results

    # Denne rutinen lager liste over de som er kommet i mål.
    # Den skal inneholde følgende: klasse, plassering, tid osv...
    def make_finish_list(self):
        # Finn alle klasser
        # Hent liste fra alle klasse
        # Lag liste
        # Sorter liste
        # print(sorted(liste, key=lambda i: i['Innkomst']))

        print('Hello')

    # DEnne gjelder kun for Poeng-O
    def set_poengo_text(self,name):
        #print(name)
        return {
            'Startnr': str(' '),
            'Plass': name[0],
            'Navn': name[1],
            'Klubb': name[2],
            'Tid': str(name[3]),
            'Poengsum': str(name[4]),
            'Postpoeng': str(name[5]),
            'Strekkpoeng': str(name[6]),
            'Bonuspoeng': str(name[7]),
            'Tidstraff': str(name[8]),
            'tag':str(name[11]),
        }


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
                'Poster': name[17],
                'Innkomst': name[12]
                 }
                 # Disse under brukes kun hvis det blir krøll over
         # Disse under brukes kun hvis det blir krøll over
        if name[14]: #Sjekker at løper har startid
            text['Starttid']= str(name[14].strftime('%H:%M'))
        if not text['Startnr']:
            text['Startnr'] = ' '
        if not text['Brikkenr']:
            text['Brikkenr'] = ' '
        if not text['Starttid']:
            text['Starttid'] = ''
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


