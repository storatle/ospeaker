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

    def make_last_list(self, *args):
        ute = []
        dns = []
        dsq = []
        arr = []
        names = []
        last_list = []
        self.get_names()
        names = self.runners # alle løpere
        for name in names:
            text = self.set_runner_details(name);
            text['tag'] = self.set_tag(name[10])
            if text['tag'] == 'inne':
                if name[12]:
                    text['tag'] = self.check_inn_time(name[12])
            if text['tag'] == 'dns':
                text['Tid'] = str('DNS')
                dns.append(text)
                continue
            if text['tag'] == 'ute':
                ute.append(text)
            if text['tag'] == 'dsq':
                text['Tid'] = str('DSQ')
                dsq.append(text)
            last_list.append(text)
            
        last_list = (sorted(last_list, key=lambda i: str(i['Innkomst']), reverse=True))
#        last_list.extend(dsq)
        last_list.extend(dns)
        last_list.extend(arr)
        liste=[x for x in last_list if x not in ute]
        #print(liste)
        return liste
    
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


    def make_99_list(self):
        codes= None
        all_codes = {}
        fail = []
        self.get_names();
        names = self.runners # alle løpere
        race = self.race
        #print(race)
        print('-------------------------------------------------')
        x = race[2]
        print(x.strftime("%d-%m-%y") + ' '+race[1])
        for name in names: # for hver løper
            startTid = name[18]
            #print(name)
            items = self.set_runner_details(name)
            codes = items['Poster']
            #print(items['Starttid'])
            times = items['Times']
            if (codes != None):
                codes = codes.split()
                times = times.split()
                times = [y.replace(',', '') for y in times]
                #print(codes)
                for code in codes:
                    #print(code)
                    if (code not in all_codes):
                        all_codes[code] = {}
                        all_codes[code]['num'] = 0 
                        all_codes[code]['times'] = {}
                        all_codes[code]['99'] = False
                    all_codes[code]['num'] += 1
                    ind = times.index(code)
                    #print(code)
                    num = (all_codes[code]['num'])
                    all_codes[code]['times'][num] = startTid + timedelta(0, int(times[ind+1]))
            if (times != None):
                #print(times)
                if ('99' in times ):
                     ind = times.index('99')-2 # Hva om det er flere?
                     if (times[ind] not in fail):
                         #print(times[ind])
                         all_codes[times[ind]]['99'] = True
                         #print('kode 99 på ' + times[ind])
                         fail.append(times[ind])
                     #code = codes[ind]
        #sorted_keys = sorted(all_codes, key=lambda x: (all_codes[x]['num']))
        #print(sorted_keys)
        #print(names)
        #d = all_codes
        #items = sorted(d.items(), key = lambda tup: {tup[1]['num'], tup[1]['99']})
        #print(items)
        #print(all_codes)
        #all_codes = sorted(all_codes.items(), key=lambda x: x[1]['num'], reverse=True)
        #all_codes = all_codes[0]
        #print(all_codes)
        for key in all_codes:
            error = ''
            #print(all_codes[key]['99'])
            if (all_codes[key]['99']):
                error = ' - 99'
            print(key + ': ' + str(all_codes[key]['num']) +error ) #+ ': ' + all_codes[key]['99'])
       # for key in all_codes:
       #     string = ''
       #     times = all_codes[key]['times']
       #     for t in times:
       #         d = datetime(times[t].year, times[t].month, times[t].day).timestamp()
       #         time = str(times[t].timestamp() -d)
       #         string = string + ',' + time
       #     print(key + string)


    # lager liste over PoengO
    def make_point_list(self):
        climb_time = ''
        sprint_time = ''
        data = poengo.data
        maxtime = poengo.data()['maxtime']
        overtime_penalty = poengo.data()['overtime_penalty']
        control_point = poengo.data()['control_point']
        race_controls = poengo.data()['race_controls']
        race_controls = race_controls.split()
        bonus_tracks = poengo.data()['bonus_tracks']
        bonus_tracks = bonus_tracks.split()
        climb_track = poengo.climb()['climb']
        sprint_track = poengo.sprint()['sprint']
        #print(bonus_tracks)
        #climb_track = poengo.data()['climb_track']
        #climb_track = climb_track.split()
        #print(climb_track)
        #sprint_track = poengo.data()['sprint_track']
        #sprint_track = sprint_track.split()
        #print(sprint_track)
        ##race_controls = [str(i) for i in race_controls],'Klatrestrekk','Sprint'
        self.heading = ['Plass','Navn', 'Klubb','Tid', 'Sprint','Klatrestrekk','Poengsum','Postpoeng','Strekkpoeng','Bonuspoeng','Tidsstraff','sprintsek','klatresek']
        self.get_names()
        names = self.runners
        results = []
        self.heading.extend(race_controls)
        self.heading.extend(bonus_tracks)
        for name in names:
            sprint_time = ''
            climb_time = ''
            sprint_lap = 10000;
            climb_lap = 10000;
            sum_points = 0
            time_penalty = 0
            control_points = 0
            track_points = 0
            climb_points = 0
            bonus = 0
            text = self.set_runner_details(name)
            text['Tid'] = name[8]
            text['tag'] = self.set_tag(name[10])
            codesandtimes = name[11].split()
            #print(codesandtimes)
            if text['Tid']:
                controls= list(text['Poster'].split())
                #print(controls)
                #controls = list(set(controls))
                #print(controls)
                controls = [x for x in controls if x != '99']
                controls = [x for x in controls if x != '250']
                #controls = [x for x in controls if x != '100']
                control_points =  -control_point #Trekker i fra en post siden mål er med på spurtstrekker
                text['Poster'] = controls
                # print(controls)
                # Fills in with all race control codes into text and set them to ""
                for code in race_controls:
                    if code in controls:
                        text[code] = control_point
                        control_points = control_points + control_point
                    else:
                        text[code] = str('')
                sum_points = control_points# - control_point #Trekker ifra mål. Må ha me mål når jeg har sprintpoeng
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
                        #print(controls)
                        #print(track)
                        if (track[0] in controls) and (track[1] in controls):
                            ind = controls.index(track[1]) - controls.index(track[0])
                            if ind == 1:
                                track_points = track_points + track[2]
                                text[track[0] + "->" + track[1]] = track[2]
                                if (track[0] in climb_track) and (track[1] in climb_track):
                                    i1 = codesandtimes.index(track[0])+1
                                    i2 = codesandtimes.index(track[1])+1
                                    t1 = int(codesandtimes[i1][:-1])
                                    t2 = int(codesandtimes[i2][:-1])
                                    climb_lap = t2-t1
                                    m,s = divmod(climb_lap,60);
                                    climb_time = f'{m:02d}:{s:02d}' 
                                    #print(f'{m:02d}:{s:02d}')  
                                    #print(climb_time)
                                if (track[0] in sprint_track) and (track[1] in sprint_track):
                                    i1 = codesandtimes.index(track[0])+1
                                    i2 = codesandtimes.index(track[1])+1
                                    t1 = int(codesandtimes[i1][:-1])
                                    t2 = int(codesandtimes[i2][:-1])
                                    sprint_lap = t2-t1
                                    m,s = divmod(sprint_lap,60);
                                    sprint_time = f'{m:02d}:{s:02d}' 
                                    #print(f'{m:02d}:{s:02d}')  
                                    #print(sprint_time)
                    sum_points = sum_points + track_points
                except Exception:
                    text['Strekkpoeng']=str('')

                text['sprintsek'] = sprint_lap
                text['klatresek'] = climb_lap
                text['Klatrestrekk'] = climb_time
                text['Sprint'] = sprint_time
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

        results = sorted(results, key=lambda tup: (tup[12]) ) # sorter på climb_tid
        vinner = results[0][1]
        results[0][6] = results[0][6] + 100
        plass= 1
        point = ''   
        
        for result in results:
            if (result[5] != point):
                if (result[5] != ''):
                    result[5] = result[5] +' ('+ str(plass)+')'
            plass +=1
            point = result[5]
        results = sorted(results, key=lambda tup: (tup[11]) ) # sorter på sprint_time
        if (results[0][1] == vinner):
            results[1][6] = results[1][6] + 100
        else:
            results[0][6] = results[0][6] + 100
        plass= 1
        point = ''
        for result in results:
            if (result[4] != point):
                if (result[4] != ''):
                    result[4] = result[4] +' ('+ str(plass)+ ')'
            plass +=1
            point = result[4]

        results = sorted(results, key=lambda tup: (tup[6]) , reverse=True)
        plass=1
        point = ''
        for result in results:
            if (result[6] == point):
                result[0] = ''
            else:
                result[0] = plass
            plass +=1
            point = result[6]
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
            #'Klubb': name[2],
            'Tid': str(name[3]),
            'Sprint': str(name[4]),
            'Klatring': str(name[5]),
            'Poengsum': str(name[6]),
            'Postpoeng': str(name[7]),
            'Strekkpoeng': str(name[8]),
            'Bonuspoeng': str(name[9]),
            'Tidstraff': str(name[10]),
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
                'Innkomst': name[12],
                'Times' : name[11] # Koder, tid og 99
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
        
    def check_inn_time(self, inntime):
#        print(inntime)
        if inntime:
            if (datetime.now() + timedelta(minutes=-1) <= inntime):
                return 'last'
            else:
                return 'inne'


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


