#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
#from tkFileDialog import askopenfilename  # , asksaveasfilename
from functools import partial
#from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
#from reportlab.pdfgen import canvas as cv
import os
#from reportlab.graphics import renderPDF
#from svglib.svglib import svg2rlg
import random
#from tkinter.ttk import *
#from tkinter import filedialog

#import dialogBoxes3
# import sys
import time
from datetime import datetime, timedelta
import config
import heading
import pdfgen

#import MySQLdb
import pymysql
#import sqlite3


class Database:
    def __init__(self):
        self.num=1
        self.db = pymysql.connect(**config.get_config(self.num))
        self.races = []
        self.race_ids = []
        self.cursor = self.db.cursor()
        #self.read_version()
        self.read_races()
        #self.read_classes()
        #self.read_names()
        #self.names = None

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
            print("Error: unable to fecth data")

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
            print("Error: unable to fecth names")


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
            print("Error: unable to fecth names")

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
            print("Error: unable to fecth classes")

class Event:

    def __init__(self, db , num):
        self.runners = []
        self.classes = []
        self.class_names=[]
        self.db = db
        self.get_event(num)
        #self.get_names()
        self.get_classes()

    def get_event(self, event):
        #print(event)
        self.race = self.db.races[event]
        self.race_id = self.race[0]
        self.race_name = self.race[1]

    def get_names(self):
        self.runners=self.db.read_names(self.race_id)
        #self.runners = self.db.names

        # for name in self.db.names:
        #     if name[15] == self.race_id:
        #         self.runners.append(name)
        #         #print(name[2])

    def get_classes(self):
        self.db.read_classes(self.race_id)
        for row in self.db.classes:
            if row[6] == self.race_id:
                if row[14] == 0:
                    self.class_names.append(row[1])
                    self.classes.append(row)
                    #print(row[1])

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
        urangert = False
        uten_tid = False
        starts = []
        vinnertid = None
        start_list = []
        dns = []
        dsq = []
        plass = 0
        # self.db.update_db()
        # vis regulær startlister

        data = self.find_class(class_name)
        #self.b.tree.delete(*self.b.tree.get_children())
        #self.a.tree.delete(*self.a.tree.get_children())
        if data:
            data = sorted(data, key=lambda tup: str(tup[14]))  # , reverse=True)
            for name in data:
                name = list(name)
                if not name[6]:
                    name[6] = ' '
                if not name[7]:
                    name[7] = ' '

                if name[14]:
                    text = [str(name[7]), str(name[6]), name[2], name[3], self.find_class_name(name[4]),
                            str(name[14].strftime("%H:%M")), str(name[8]),
                            str(' '), name[10]]
                else:
                    text = [str(name[7]), str(name[6]), name[2], name[3], self.find_class_name(name[4]),
                            str(' '), str(name[8]),
                            str(' '), name[10]]
                start_list.append(text)

        return start_list

    # Sett et flagg her hvis denne skal brukes på oppdatere outlist. Da returnerer du out i stedet for result
    def make_result_list(self, class_name, *args):
        urangert = False
        uten_tid = False
        results = []
        vinnertid = None
        result_list = []
        ute = []
        dns = []
        dsq = []
        plass = 0
        # Henter inn alle navn i klassen
        data = self.find_class(class_name)
        for name in data:
            # name[2] = navn, name[3] = klubb, name[7] = startnummer, name[8] = sluttid, /
            # name[10] = tag, name[14] = startid
            name = list(name)
            #Setter tag
            name[10] = set_tag(name[10])
            # sjekker om løperen ikke er kommet i mål.
            if not name[8] or name[10] =='ute':
                #Regner ut tiden som skal vises i Vindu. Ikke på resultatlister
                name[8] = get_time(name[14])
            results.append(name)

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
            text = {
                    'Startnr': name[7],
                    'Plass':str(''),
                    'Navn': name[2],
                    'Klubb': name[3],
                    'Tid': str(name[8]),
                    'Diff':str(''),
                    'Klasse':class_name,
                    'Starttid':str(name[14].time()),
                    'tag':name[10]i
                    'Brikkenr':str('')
                    }
            # Sjekker om løperen ikke er disket eller ikke har startet eller er arrangør
            # Endrer til å sjekke om løperen er inne:
            #if not (name[10] == 'dsq' or name[10] == 'dns' or name[10] == 'arr' or name[10] == 'ute'):
            #Sjekker om løper har kommet i mål
            #if text['tag'] == 'inne':
                # Det er mulig denne kan droppes hvis det leses direkte inn hvid tiden er tom
            if name[14]: #Sjekker at løper har startid
                text['Starttid']= str(name[14].time())
            elif uten_tid:
                text['Tid'] = str('fullført')
            elif text['tag'] == 'ute':
                ute.append(text)
            elif text['tag'] == 'dsq':
                text['Tid'] == str('DSQ')
                dsq.append(text)
            elif text['tag'] == 'dns':
                text['Tid'] == str('DNS')
                dns.append(text)
            elif not vinnertid:
                # Setter vinnertiden til øverste på lista siden den er sortert
                vinnertid = name[8]
            elif urangert:
                result_list.append(text)
            else:
                plass += 1
                text['Plass']=str(plass)
                # Finner differansen
                diff = name[8] - vinnertid
                text['Diff'] = str(diff)
                result_list.append(text)
        result_list.extend(dsq)
        result_list.extend(dns)
        if args == out:
            return ute
        else:
            return result_list

class gui:

    def __init__(self):
        self.pdf = pdfgen.Pdf()
        self.db = Database()
        #self.spurt = 0
        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None
        self.window = tk.Tk()  # Create a window
        self.window.title("O-speaker")  # Set title
        self.window.geometry('{}x{}'.format(1700, 1000))
        self.page_break = tk.BooleanVar()
        self.one_active_class = tk.BooleanVar()
        # file-Meny 
        self.menubar = tk.Menu(self.window)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)

        try:
            self.window.config(menu=self.menubar)
        except AttributeError:
            print('Error')
            # master is a toplevel window (Python 1.4/Tkinter 1.63)

        # create all of the main containers
        top_frame = tk.Frame(self.window, width=450, height=50)  # , pady=3)
        center = tk.Frame(self.window, width=50, height=40)  # , padx=3, pady=3)
        btm_frame = tk.Frame(self.window, width=450, height=45)  # , pady=3)
        btm_frame2 = tk.Frame(self.window, width=450, height=60)  # , pady=3)

        # layout all of the main containers
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=3, sticky="ew")
        btm_frame2.grid(row=4, sticky="ew")

        # create the widgets for the top frame
        # tk.Label(top_frame, text="Startnr i mål:").grid(row=0, sticky='w')
        #self.e = tk.Entry(top_frame, font="Helvetica 30 bold", width=10)
        #self.e.bind('<Return>', self.find_runner)

        # LAbel til Combobox
        tk.Label(top_frame, text="Løp:").grid(row=0, column=1, sticky='w')

        # Combobox med alle løp i databasen
        self.combo_races = TTK.Combobox(top_frame, width=30, values=list(zip(*self.db.races))[1])
        self.combo_races.grid(row=0, column=2, sticky='w')
        self.combo_races.bind("<<ComboboxSelected>>", self.get_event, "+")
        
        # Checkboxes
        # Setter om det skal være sideskift for printing
        self.check = tk.Checkbutton(top_frame, text="Print med sideskift", variable=self.page_break).grid(row=0, column=3, sticky='w')
        self.check2 = tk.Checkbutton(top_frame, text="Print aktiv_klasse", variable=self.one_active_class).grid(row=0, column=4, sticky='w')
        
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
        self.a = Window(self.ctr_mid)
        self.a.tree.bind("<Double-1>", self.onclick_a)

        # Tabell i nederste vindu
        self.b = Window(self.ctr_mid)
        #self.b.tree.bind("<Double-1>", self.onclick_b)

        # frame.pack()
        self.window.mainloop() # Create an event loop

    def get_event(self, event):
        # Henter ønsket løp fra Combobox
        self.race = Event(self.db, self.combo_races.current())
        # Lager PDF meny
        pdf_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="PDF", menu=pdf_menu)
        pdf_menu.add_command(label="Lag startliste", command=self.pdf_start_list)#(self.race,False,self.one_active_class,self.page_break))
        pdf_menu.add_command(label="Lag startliste for start", command=self.pdf_start_list_for_start)#(self.race, True, self.one_active_class, self.page_break))
        pdf_menu.add_separator()
        pdf_menu.add_command(label="Lag resultatliste", command=self.pdf_result_list)#(self.race, self.one_active_class, self.page_break))

        try:
            self.window.config(menu=self.menubar)
        except AttributeError:
            print('Error')

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
        self.window.mainloop()

    # Denne laget jeg for å få til å bruke meny, men kanskje jeg kan bruke følgende funksjon i stedet
    # pdf_menu.add_command(label="Lag startliste", command=self.pdf_start_list, self.race, False, self.one_active_class, self.class_name, self.page_break)
    # Det vil i så fall kunne fjerne disse tre funksjonen under 
    def pdf_start_list(self):
        self.pdf.start_list(self.race, False, self.one_active_class.get(), self.class_name, self.page_break.get())

    def pdf_start_list_for_start(self):
        self.pdf.start_list(self.race, True, self.one_active_class.get(), self.class_name, self.page_break.get())

    def pdf_result_list(self):
        self.pdf.result_list(self.race, self.one_active_class.get(), self.class_name, self.page_break.get())


    def onclick_b(self, event):
        self.update_runner_table()

    def onclick_a(self, event):
        self.a.after_cancel(self.atree_alarm)
        item = str(self.a.tree.focus())
        #item = self.a.tree.selection()[0]
        class_name = self.a.tree.item(item, "value")[2]
        self.write_result_list(class_name)
        self.update_runner_table()

    def dummy_func(self, name):
        print(name)

    def write_result_list(self, class_name):
        # denne kjøres kontinuerlig så og derfor må jeg sette flgg om ikke endrer urangerte listeri/
        # kontinuerlig. 
        # Her setter jeg randomize lik False
        # Hvis det er H/D -10 eller N-åpen så skal det være urangerte lister
        self.randomized = False
        if self.class_name:
            self.b.after_cancel(self.btree_alarm)
            self.a.after_cancel(self.atree_alarm)

        # Her legger jeg inn en resultatliste som bare inneholder de som er ute
        self.b.tree.delete(*self.b.tree.get_children())
        out_list = self.race.make_result_list(class_name, out)
        
        out_list = self.update_out_list(class_name)
        self.write_table(out_list,'b')
        self.btree_alarm = self.b.after(200, self.write_result_list, class_name)

        # Her legger jeg inn en resultatliste som bare inneholde de som er inne, DNS og DSQ
        self.a.tree.delete(*self.a.tree.get_children())
        result_list = self.race.make_result_list(class_name)
        self.write_table(result_list,'a')
        self.atree_alarm = self.a.after(250, self.write_result_list, class_name)
        self.class_name = class_name

    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'a':
                self.a.LoadinTable(name)
            else:
                self.b.LoadinTable(name)

    # Finner løper fra Brikkesys databasen og skriver denne i øverste tabell. Løperne må ha startnummer.
    # Denne er ikke i bruk lenger. JEg bør bruke forvarsel i stedet
    def find_runner(self, event):
        if self.name:
            self.a.after_cancel(self.atree_alarm)
        self.name = self.race.find_runner(self.e.get()) #Denne bør være oppdatert fra databasen
        self.e.delete(0, 'end')
        self.load_runner(self.name)
        self.update_runner_table()

    def load_runner(self, name):
        #name = list(name)
        name = list(name)
        if not name[8]:
            name = list(name)
            name[8] = get_time(name[14])
        name[10] = set_tag(name[10])

        text = [name[7], str(' '), name[2], name[3], self.race.find_class_name(name[4]), str(name[14].time()), str(name[8]),
                str('-'), name[10]]
        self.a.LoadinTable(text)

    # Er denne i bruk mon tro?
    def update_runner_table(self):
        num_list = []
        for child in self.a.tree.get_children():
            #Henter startnummer
            num_list.append(self.a.tree.item(child)["text"])
            print(num_list)
        self.a.tree.delete(*self.a.tree.get_children())
        for num in reversed(num_list):
            name = self.race.find_runner(num)
            self.load_runner(name)
        #self.name = name
        self.atree_alarm = self.a.after(200, self.update_runner_table)
        #self.a.tree.get_children()

    def open_file(self):
        myformats = [('Startliste', '*.xml')]
        #self.name = askopenfilename(filetypes=myformats, title="Open result file")
        file = open(self.name, 'r')
        tree = ET.parse(file)
        self.root = tree.getroot()
        self.e.bind('<Return>', self.find_runner)

    def set_spurttid(self):
        # self.canvas.fixpoints=self.fixpoints
        #self.d = dialogBoxes.set_spurttid(self.canvas)
        self.spurt = self.d.result

class Window(TTK.Frame):

    def __init__(self, parent):
        TTK.Frame.__init__(self, parent)
        self.num_lines =10 
        self.tree = self.CreateUI()

        self.tree.tag_configure('ute', background='orange')
        #self.tree.tag_configure('inne', background='white')
        self.tree.tag_configure('inne', background="red")
        self.tree.tag_configure('dsq', background='red')
        self.tree.tag_configure('dns', background='grey')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky=('n')) #N, S, W, E))
        #parent.grid_rowconfigure(2, weight=1)
        #parent.grid_columnconfigure(2, weight=1)

    def CreateUI(self):
        style = TTK.Style()
        style.configure('Treeview', rowheight=40, font="Helvetica 20 bold")  # SOLUTION
        tv = TTK.Treeview(self, height=self.num_lines, style='Treeview')

        vsb = TTK.Scrollbar(self, orient="vertical", command=tv.yview)
        vsb.place(x=30+1556, y=20, height=400)

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
        #self.treeview.insert('', 'end', text="First", values=('10:01','10:11', 'Ok'))

    def LoadinTable(self, entry):
       # print(entry)

        # Sjekker om de har startnummer, dette trenger jeg vel ikke lenger?
        if not entry['startnummer']:
            entry['startnummer'] = ' '
        # Denne må endres hvis jeg skal bruke event.make_resultlist
        # self.tree.insert('', 0, text=entry[0], values=(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]), tags = (entry[8],))

       # Mangler starnummer!
        self.tree.insert('', 0, text=entry['startnummer'], values=(entry['plass'], entry['navn'], entry['klubb'], entry['klasse'], entry['starttid'], entry['tid'], entry['differanse']), tags = (entry['tag'],))

def main():

    #o_event.find_names()
    #o_event.get_classes()
    #o_event.print_class(782)
    db = Database()
    #self.race = Event(db, self.combo_races.current())
    o_event = Event(db, 130)
    #o_event.get_event(130)
    #pdf_list(o_event)
    gui()


def pdf_list(event):
    pdf = pdfgen.Pdf()
    pdf.start_list(event)
    pdf.result_list(event)



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

    out = ' '
    return out


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
    else:
        print("Finner ikke tag")

main()  # Create GUI


# Denne leser startliste fra tekst. Dette er midlertidig for å unngå å bruke mysql
            # with open('startlist.txt') as f:
            #     for line in f:
            #         start_list.append(line[1:-2].split(','))
