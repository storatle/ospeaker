#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from functools import partial
import os
import random
import time
from datetime import datetime, timedelta
import ospeaker_config as config
import heading
import pdfgen
import pymysql
import argparse


class Database:
    def __init__(self, ip_adress):
        self.ip= ip_adress
        self.db = pymysql.connect(**config.get_config(self.ip))
        self.races = []
        self.race_ids = []
        self.cursor = self.db.cursor()
        try:
            self.read_races()
        except:
            log_file.write("No races in database {0}: {1}\n".format(str(self.ip), str(self.ip)))
            log_file.flush()
    def update_db(self):
        db = pymysql.connect(**config.get_config(self.num))

    def read_version(self):
        # execute SQL query using execute() method.
        self.cursor.execute("SELECT VERSION()")

        # Fetch a single row using fetchone() method.
        data = self.cursor.fetchone()
        print("Database version : %s " % data)

    # Henter alle løp
    def read_races(self):

        sql = " SELECT * FROM RACES"
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            self.races = self.cursor.fetchall()

        except Exception:
            sql = " SELECT * FROM races"
            self.cursor.execute(sql)
            self.races = self.cursor.fetchall()

        except :
            log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
            log_file.flush()

    # Henter alle løpernavn
    def read_names(self, race_id):
        self.db.commit()

        try:
            sql = " SELECT * FROM NAMES WHERE RACEID = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            #self.names = self.cursor.fetchall()
            return self.cursor.fetchall()

        except Exception:
            sql = " SELECT * FROM names WHERE raceid = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            # self.names = self.cursor.fetchall()
            return self.cursor.fetchall()

        except:
            log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
    def read_names_from_class(self, race_id,class_id):
        self.db.commit()

        try:
            sql = " SELECT * FROM NAMES WHERE RACEID = %(race_id)s AND CLASSID = %(class_id)s"
            self.cursor.execute(sql, {'race_id': race_id, 'class_id': class_id})
            # Fetch all the rows in a list of lists.

            return self.cursor.fetchall()

        except Exception:

            sql = " SELECT * FROM names WHERE raceid = %(race_id)s AND classid = %(class_id)s"
            self.cursor.execute(sql, {'race_id': race_id, 'class_id': class_id})
            # Fetch all the rows in a list of lists.

            return self.cursor.fetchall()

        except:
            log_file.write("Unable to fetch names {0}:{1} \n".format(str(sql)), str(class_id))
            log_file.flush()
    # Henter alle Klasser
    def read_classes(self,race_id):

        try:
            sql = " SELECT * FROM CLASSES WHERE RACEID = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            self.classes = self.cursor.fetchall()
            # for row in classes:

        except Exception:
            sql = " SELECT * FROM classes WHERE raceid = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            self.classes = self.cursor.fetchall()

        except:
            log_file.write("Unable to fetch names {0}:{1} \n".format(str(sql)), str(class_id))
            log_file.flush()

    # Henter startnummber fra starnummerdatabasen 
    def read_start_numbers(self):
        self.db.commit()
        sql = " SELECT * FROM startnumbers"
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            return self.cursor.fetchall()

        except Exception:
            sql = " SELECT * FROM STARTNUMBERS"
            self.cursor.execute(sql)
            return self.cursor.fetchall()

        except:
            log_file.write("Unable to fetch data:  {0}: \n".format(str(sql)))
            log.file.flush()
class Race:

    def __init__(self, db , num):
        self.runners = []
        self.classes = []
        self.class_names=[]
        self.db = db
        #print(num)
        self.get_race(num)
        self.get_classes()

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
            name[10] = set_tag(name[10])
            # sjekker om løperen ikke er kommet i mål.
            if not name[8] or name[10] =='ute':
                #Regner ut tiden som skal vises i Vindu. Ikke på resultatlister
                name[8] = get_time(name[14])
            results.append(name)

        # Disse klassene bør sette i en egen config_fil
        # Her må jeg ha et flagg som sier at klasser ikke skal sortere lista
        # H 10 og D 10 skal ha urangerte lister, men det kan være med tider
        # N-åpen skal ikke ha tider bare ha fullført 
        # H/D 11-12N kan ha rangerte lister
        if (class_name == 'H -10' or class_name == 'D -10'): 
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
                diff = name[8] - vinnertid
                text['Diff'] = str(diff)
                
                # regner ut poeng for løperen
                text['Poeng'] = 100 * 50 * (name[8]-vinnertid) / vinnertid
                if text['Poeng'] <= 50:
                    text['Poeng'] = 50

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
        return text
        

    def calc_points(results):
        # Bør jeg bare flytte denne inn i ospeaker?
        # Og så kan jeg lage en egen utskriftsmodul for poengberegninger i pdfgen.py
        # Finner tid til første løper og setter den som vinnertid
        vinnertid = results[0]['Tid'] # Er denne string nå? Den må endres til vanlig tid
        for runner in results:
            runner['Poeng'] = 100 * 50 * (runner['Tid']-vinnertid) / vinnertid
            if runner['Poeng'] <= 50:
                runner['Poeng'] = 50
       



class Window(tk.Tk):
    def __init__(self,*args,**kwargs):
       tk.Tk.__init__(self,*args,**kwargs)
       self.notebook = TTK.Notebook()
       self.add_tab()
       self.notebook.grid(row=0)
  
    def add_tab(self):
        tab = Results(self.notebook)
        tab2 = Prewarn(self.notebook) 
        self.notebook.add(tab,text="Resultater")
        self.notebook.add(tab2,text="Forvarsel")
  
  
class Results(tk.Frame):
    def __init__(self,name,*args,**kwargs):
        tk.Frame.__init__(self,*args,**kwargs)
        self.db = Database(res_db)
        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None
        global page_break
        global one_active_class
        global for_start
        page_break = tk.BooleanVar()
        one_active_class = tk. BooleanVar()
        for_start = tk.BooleanVar()

        # create all of the main containers
        top_frame = tk.Frame(self, width=450, height=50)  # , pady=3)
        center = tk.Frame(self, width=50, height=40)  # , padx=3, pady=3)
        btm_frame = tk.Frame(self, width=450, height=45)  # , pady=3)
        btm_frame2 = tk.Frame(self, width=450, height=60)  # , pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=3, sticky="ew")
        btm_frame2.grid(row=4, sticky="ew")

        # Label til Combobox
        tk.Label(top_frame, text="Løp:").grid(row=0, column=1, sticky='w')
        # Combobox med alle løp i databasen
        self.combo_races = TTK.Combobox(top_frame, width=30, values=list(zip(*self.db.races))[1])
        self.combo_races.grid(row=0, column=2, sticky='w')
        self.combo_races.bind("<<ComboboxSelected>>", self.get_race, "+")
        
        # Checkboxes
        # Setter om det skal være sideskift for printing
        self.check = tk.Checkbutton(top_frame, text="Print med sideskift", variable=page_break).grid(row=0, column=3, sticky='w')
        self.check2 = tk.Checkbutton(top_frame, text="Print aktiv_klasse", variable=one_active_class).grid(row=0, column=4, sticky='w')
        self.check3 = tk.Checkbutton(top_frame, text="Print lister for start", variable=for_start).grid(row=0, column=5, sticky='w')

        # create the center widgets
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(1, weight=1)

        self.ctr_left = tk.Frame(center, width=100, height=290)
        self.ctr_mid = tk.Frame(center, width=250, height=290)  # , padx=3, pady=3)
        self.ctr_right = tk.Frame(center, width=100, height=190)  # , padx=3, pady=3)
        
        self.ctr_left.grid(row=0, column=0, sticky="ns")
        self.ctr_mid.grid(row=0, column=1, sticky="nsew")
        self.ctr_right.grid(row=1, column=1, sticky="nsew")

        # Tabell i øverste vindu
        self.res = Table(self.ctr_mid, 10)
        self.res.tree.bind("<Double-1>", self.onclick_res)

        # Tabell i nederste vindu
        self.out = Table(self.ctr_mid, 10)
        self.out.tree.bind("<Double-1>", self.onclick_out)
        self.name = name


    def get_race(self, race):
        # Henter ønsket løp fra Combobox
        self.race = Race(self.db, self.combo_races.current())
        global race_number
        race_number = self.combo_races.current()
        # Lager knapper for hver klasse
        try:
           if self.button:
                for knapp in self.button:
                    knapp.grid_remove()
        except:
            self.button = list()
        i = 1
        j = 0
        for class_name in self.race.class_names:
 
            self.button.append(tk.Button(self.ctr_left, text=class_name, command=partial(self.write_result_list, class_name)))
            self.button[-1].grid(row=i, column=j)
            i += 1
            if i >= 30:
                j = 1
                i = 1

    def write_result_list(self, class_name):
        global active_class
        active_class = class_name
        # denne kjøres kontinuerlig så og derfor må jeg sette flagg om ikke endrer urangerte listeri/
        # kontinuerlig. Her setter jeg randomize lik False
        self.randomized = False
        if self.class_name:
            self.res.after_cancel(self.res_tree_alarm)
            self.out.after_cancel(self.out_tree_alarm)

        # Her legger jeg inn en resultatliste som bare inneholde de som er i mål, DNS og DSQ
        self.res.tree.delete(*self.res.tree.get_children())
        result_list = self.race.make_result_list(class_name)
        self.write_table(result_list,'res')
        self.res_tree_alarm = self.res.after(200, self.write_result_list, class_name)
        self.class_name = class_name

        # Her legger jeg inn en resultatliste som bare inneholder de som er ute
        self.out.tree.delete(*self.out.tree.get_children())
        out_list = self.race.make_result_list(class_name, 'out')
        self.write_table(out_list,'out')
        self.out_tree_alarm = self.out.after(250, self.write_result_list, class_name)

    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'res':
                self.res.LoadinTable(name)
            else:
                self.out.LoadinTable(name)

    # Denne brukes når det dobbelklikkes på navn i tabellen. Foreløpig så skjer det ingen ting. peker til update runners som er kommentert ut under.    
    def onclick_out(self, race):
        self.update_runner_table()
 
    # Denne brukes når det dobbelklikkes på navn i tabellen. Foreløpig så skjer det ingen ting. peker til update runners som er kommentert ut under.    
    def onclick_res(self, race):
        #self.res.after_cancel(self.res_tree_alarm)
        #item = str(self.res.tree.focus())
        #class_name = self.res.tree.item(item, "value")[2]
        #self.write_result_list(class_name)
        self.update_runner_table()
  
 
class Prewarn(tk.Frame):
    def __init__(self,name,*args,**kwargs):
        tk.Frame.__init__(self,*args,**kwargs)
        self.res_db = Database(res_db)
        self.pre_db = Database(pre_db)
        self.idx = 0
        self.runners = []
        top_frame = tk.Frame(self, width=450, height=50)  # , pady=3)
        center = tk.Frame(self, width=50, height=40)  # , padx=3, pady=3)
        btm_frame = tk.Frame(self, width=450, height=45)  # , pady=3)
        btm_frame2 = tk.Frame(self, width=450, height=60)  # , pady=3)

        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=3, sticky="ew")
        btm_frame2.grid(row=4, sticky="ew")

        # create the center widgets
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(1, weight=1)

        self.ctr_left = tk.Frame(center, width=100, height=290)
        self.ctr_mid = tk.Frame(center, width=250, height=290)  # , padx=3, pady=3)
        self.ctr_right = tk.Frame(center, width=100, height=190)  # , padx=3, pady=3)
         
        self.ctr_left.grid(row=0, column=0, sticky="ns")
        self.ctr_mid.grid(row=0, column=1, sticky="nsew")
        self.ctr_right.grid(row=1, column=1, sticky="nsew")

        self.button=tk.Button(top_frame, text='start forvarsel',  command=partial(self.write_prewarn_list))
        self.button.grid(row=0,column=0)
        # Tabell i øverste vindu
        self.pre = Table(self.ctr_mid, 20)
        self.pre.tree.bind("<Double-1>", self.onclick_pre)

    def write_prewarn_list(self):
        prewarn_list= []
        self.race = Race(self.res_db, race_number)

        # Her legger jeg inn en resultatliste som bare inneholde de som er i mål, DNS og DSQ
        self.pre.tree.delete(*self.pre.tree.get_children())
        self.find_runner()
       
        for runner in self.runners:
            runner = list(runner)
            runner[10] = set_tag(runner[10])
            # sjekker om løperen ikke er kommet i mål.

            #if not runner[8] or runner[10] =='ute':
            if runner[10] =='ute':
                #Regner ut tiden som skal vises i Vindu. Ikke på resultatlister
                try:
                    runner[8] = get_time(runner[14])
                except:
                    if runner[10] == 'dns':
                        runner[8] = 'DNS'
            if not runner[8]:
                runner[8] = runner[10]

            #   print('Cannot get time')
            prewarn_list.insert(0,self.race.set_runner_details(runner))

        self.write_table(prewarn_list,'pre')
        self.pre_tree_alarm = self.pre.after(200, self.write_prewarn_list)


    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'res':
                self.res.LoadinTable(name)
            elif table == 'pre':
                self.pre.LoadinTable(name)
            else:
                self.out.LoadinTable(name)

    # Denne brukes når det dobbelklikkes på navn i tabellen. Foreløpig så skjer det ingen ting. peker til update runners som er kommentert ut under.    
    def onclick_pre(self, race):
        self.update_runner_table()

    # Finner løper fra Brikkesys databasen og skriver denne i øverste tabell. Løperne må ha startnummer.
    def find_runner(self):
        nums = self.pre_db.read_start_numbers()
        for num in nums:
            if self.idx < num[0]:
                self.idx = num[0]
                try:
                    start_num = int(num[1])
                    runner = self.race.find_runner(start_num)
                    if runner:
                        self.runners.append(runner)
                except:
                    str_num = num
                    log_file.write("No startnumbers {0}: \n".format(str(num)))

class Table(TTK.Frame):

    def __init__(self, parent, rows):
        TTK.Frame.__init__(self, parent)
        self.rows = rows
        self.rowheight = 40
        self.tree = self.CreateUI()

        self.tree.tag_configure('ute', background='orange')
        self.tree.tag_configure('inne', background="white")
        self.tree.tag_configure('dsq', background='red')
        self.tree.tag_configure('dns', background='grey')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky=('n')) #N, S, W, E))

    def CreateUI(self):
        style = TTK.Style()
        style.configure('Treeview', rowheight=self.rowheight, font="Helvetica 20 bold")  # SOLUTION
        tv = TTK.Treeview(self, height=self.rows, style='Treeview')

        vsb = TTK.Scrollbar(self, orient="vertical", command=tv.yview)
        vsb.place(x=30+1556, y=20, height=self.rowheight*self.rows)

        tv.configure(yscrollcommand=vsb.set)
        tv['columns'] = ('plass', 'navn', 'klubb', 'klasse', 'starttid', 'tid', 'diff')
        tv.heading("#0", text='Startnum', anchor='w')
        tv.column("#0", anchor="center", width=100)
        tv.heading('plass', text='Plass')
        tv.column('plass', anchor='w', width=100)
        tv.heading('navn', text='Navn')
        tv.column('navn', anchor='w', width=400)
        tv.heading('klubb', text='Klubb')
        tv.column('klubb', anchor='center', width=300)
        tv.heading('klasse', text='Klasse')
        tv.column('klasse', anchor='center', width=200)
        tv.heading('starttid', text='Starttid')
        tv.column('starttid', anchor='center', width=150)
        tv.heading('tid', text='Tid')
        tv.column('tid', anchor='center', width=150)
        tv.heading('diff', text='Differanse')
        tv.column('diff', anchor='center', width=200)
        tv.grid(sticky=('n'))#, 'S', 'W', 'E'))
        return tv

    def LoadTable(self):
        self.tree.insert('', 'end', text="First", values=('10:00', '10:10', 'Ok'))

    def LoadinTable(self, entry):
       # print(entry)
        # Sjekker om de har startnummer, dette trenger jeg vel ikke lenger?
        if not entry['Startnr']:
            entry['Startnr'] = ' '
        # self.tree.insert('', 0, text=entry[0], values=(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]), tags = (entry[8],))
        self.tree.insert('', 0, text=entry['Startnr'], values=(entry['Plass'], entry['Navn'], entry['Klubb'], entry['Klasse'], entry['Starttid'], entry[str('Tid')], entry['Diff']), tags = (entry['tag'],))

def main():

#    pdf = pdfgen.Pdf()
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', help='Server med brikkesys, local, Klara, Milo eller Prewarn')
    args = parser.parse_args()

    global active_class
    global res_db
    global pre_db
    global log_file
 
    if args.server:
        res_db = args.server
    else:
        res_db = 'local'
    log_file = open("ospeaker.log", "w")
    pre_db = 'Prewarn'
    my_app = Window()
    my_app.geometry('1700x1000')
    menubar = tk.Menu(my_app)

    # file-Meny 
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Open...", command=dummy_func)#,'Open file....')
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=my_app.quit)
    #my_app.notebook.tab(0).page_break
    one_active_class = True
    class_name = True
    page_break = True

    # Lager PDF meny
    pdf_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="PDF", menu=pdf_menu)
    pdf_menu.add_command(label="Lag startliste", command=lambda: pdf_list(False)) #one_active_class, class_name, page_break))
    #pdf_menu.add_command(label="Lag startliste for start", command=lambda: pdf_list(False)) #(self.race, True, self.one_active_class, self.page_break))
    pdf_menu.add_separator()
    pdf_menu.add_command(label="Lag resultatliste", command=lambda: pdf_list(True))#(self.race, self.one_active_class, self.page_break))

    try:
        my_app.config(menu=menubar)
    except AttributeError:
        print('Error')
    my_app.mainloop()   
    #gui()
    
# Denne laget jeg for å få til å bruke meny, men kanskje jeg kan bruke følgende funksjon i stedet
# pdf_menu.add_command(label="Lag startliste", command=self.pdf_start_list, self.race, False, self.one_active_class, self.class_name, self.page_break)
# Det vil i så fall kunne fjerne disse tre funksjonen under 
def pdf_list(results):#, one_active_class, class_name, page_break):
    db = Database(res_db)
    pdf = pdfgen.Pdf()
    race = Race(db, race_number)
    if results:
        pdf.result_list(race, one_active_class.get(), active_class, page_break.get())
    else:
        pdf.start_list(race, for_start.get(), one_active_class.get(), active_class, page_break.get())

def dummy_func(self, name):
    print(name)

def get_time(starttime):
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


def set_tag(tag):
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
        log_file.write("Cannot find tag {0}: \n".format(str(tag)))
        log_file.flush()
if __name__=="__main__":
    main()  # Create GUI


