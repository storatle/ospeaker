#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
#from tkFileDialog import askopenfilename  # , asksaveasfilename
from functools import partial
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas as cv
import os
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import random

#from tkinter.ttk import *
#from tkinter import filedialog


import dialogBoxes3
# import sys
import time
from datetime import datetime, timedelta
import config

#import MySQLdb
import pymysql
#import sqlite3


# Bør ha et annet navn kanskje løpsdatabase
class Database:
    def __init__(self):
        self.num=2
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
        for id in self.classes:
            if id[1] == class_name:
                class_id = id[0]
                return self.db.read_names_from_class(self.race_id, class_id)


    # def print_class(self, class_id):
    #     for runner in self.runners:
    #         if runner[4] == class_id:
    #             print(runner[2], runner[3], self.find_class_name(runner[4]), runner[14].time(), runner[8])


        # def make_summary():
        #     f = open('gaffling.txt', 'w')
        #     p = cv.Canvas('gaffling.pdf')
        #
        #     ln = 800
        #     for side in teams:
        #         line = ' '
        #         for m in side.map:
        #             line = line + m[0:2] + '  '
        #         f.write(line + '\n')
        #         print(line)
        #         p.drawString(50, ln, 'Lag.: ' + str(side.num) + '.  ' + line)
        #         ln = ln - 15
        #     p.showPage()
        #     p.save()
        #     f.close()


class gui:

    def __init__(self):

        self.db = Database()
        self.spurt = 0
        self.class_name = None
        self.name = None
        self.print_results = False
        #self.race = Event()
        self.window = tk.Tk()  # Create a window
        self.window.title("O-speaker")  # Set title
        self.window.geometry('{}x{}'.format(1700, 1000))
        self.page_break = tk.BooleanVar()

        self.menubar = tk.Menu(self.window)
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        # menu.add_command(label="New", command=self.new_file)
        menu.add_command(label="Open...", command=self.open_file)
        menu.add_command(label="Print...", command=self.print_result_list)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.window.quit)

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
        tk.Label(top_frame, text="Startnr i mål:").grid(row=0, sticky='w')
        self.e = tk.Entry(top_frame, font="Helvetica 30 bold", width=10)
        tk.Label(top_frame, text="Løp:").grid(row=0, column=1, sticky='w')

        # Combobox med alle løp i databasen
        self.combo_races = TTK.Combobox(top_frame, width=20, values=list(zip(*self.db.races))[1])
        #self.button.append(tk.Button(top_frame, text='Resultater', command=partial(print_result_list)))


        # layout the widgets in the top frame
        self.e.grid(row=1, column=0, sticky='w')
        self.combo_races.grid(row=1, column=1, sticky='w')
        self.combo_races.bind("<<ComboboxSelected>>", self.get_event, "+")

        self.check = tk.Checkbutton(top_frame, text="Page Break", variable=self.page_break).grid(row=1, column=2, sticky='w')

        # create the center widgets
        center.grid_rowconfigure(1, weight=1)
        center.grid_columnconfigure(1, weight=1)

        self.ctr_left = tk.Frame(center, width=100, height=290)
        self.ctr_mid = tk.Frame(center, width=250, height=290)  # , padx=3, pady=3)
        self.ctr_right = tk.Frame(center, width=100, height=190)  # , padx=3, pady=3)

        self.ctr_left.grid(row=0, column=0, sticky="ns")
        self.ctr_mid.grid(row=0, column=1, sticky="nsew")
        self.ctr_right.grid(row=1, column=1, sticky="nsew")

        # # Hjemmelaget App
        self.a = App(self.ctr_mid)
        self.a.tree.bind("<Double-1>", self.onclick_a)

        self.b = App(self.ctr_mid)
        #self.b.tree.bind("<Double-1>", self.onclick_b)

        self.e.bind('<Return>', self.find_runner)
        self.spurt = 0

        # frame.pack()
        self.window.mainloop() # Create an event loop

    def print_result_list(self):
        merger = PdfFileMerger()
        #self.page_break = True # Sideskift ved ny klasse
        self.p = cv.Canvas('result.pdf')
        self.line = 750
        self.tab = [50, 250, 400, 450, 500, 800]
        self.print_heading()
        for race_class in self.race.classes:
            # Henter resultatliste for klassen
            # Her må jeg sette et flagg som forteller at den skal printes. 
            self.print_results = True
            result_list = self.update_result_list(race_class[1])
            if result_list: # Sjekker om det er deltaker i klassen
                self.active_class = result_list[0][4]
                if self.page_break.get():
                    self.print_class_heading()
                    self.print_class(result_list)
                    self.p.save()
                    merger.append(PdfFileReader('result.pdf'))
                    os.remove('result.pdf')
                    self.p = cv.Canvas('result.pdf')
                    self.line = 750
                    self.print_heading()
                else:
                    # Hvis det er en kjempestor klasse så må du printe den over flere sider. Hvis ikke så håpper du over. Sjekk lengden på en full klasse.
                    if (self.line - len(result_list) * 15-145) >= 0 or self.line > 600: # Sjekk om det er plass til en klasse på resten av siden.
                        self.print_class_heading()
                        self.print_class(result_list)
                    else:
                        self.p.showPage()
                        self.line = 750
                        self.print_heading()
                        self.print_class_heading()
                        self.print_class(result_list)

                    # if self.line < 80:
                    #     self.p.showPage()

                    # Her må du endre y slik at jeg får opphold mellom klassene.

        self.p.save()
        merger.append(PdfFileReader('result.pdf'))
        merger.write("result.pdf")

    ## Printer tittel på PDF-resultatlister
    # @param children
    # @param p reportlab.Canvas
    # @return self
    def print_heading(self):
        x = 50
        self.p.setFont('Helvetica-Bold', 14)
        self.p.drawString(300, 785, 'MELHUS ORIENTERING')
        drawing = svg2rlg('Logo MIL vektor.svg')
        renderPDF.draw(drawing, self.p, 110, 250)
        self.p.setFont('Helvetica-Bold', 12)
        self.p.drawString(x, 785, (self.race.race_name))
    ## Printer tittel på hver klasse og ved eventuelt sideskifte

    def print_class_heading(self):
        self.line = self.line - 20
        x = 50
        tab = self.tab
        # Skriver tittel for hver klasse
        self.p.setFont('Helvetica-Bold', 14)
        self.p.drawString(x, self.line, 'Klasse:')
        self.p.drawString(x + tab[0] + 5, self.line, self.active_class)
        self.line = self.line - 20
        self.p.setFont('Helvetica-Bold', 12)
        self.p.drawString(x, self.line, 'Plass')
        self.p.drawString(x + tab[0], self.line, 'Navn')
        self.p.drawString(x + tab[1], self.line, 'Klubb')
        self.p.drawCentredString(x + tab[2], self.line, 'Tid')
        self.p.drawCentredString(x + tab[3], self.line, 'Diff')
        self.line = self.line - 15


    ## Printer PDF-resultatlister for en klasse
    # @param list
    # @return self
    def print_class(self, list):
        # Get results from class
        # Skriv heading. (Plass, Navn, Klubb Tid, Diff)
        # Skriv resultatliste for klassen
        #hent klasser.
        tab = self.tab
        dy = 15
        x = 50
        i = 0
        for name in list:
            self.p.setFont('Helvetica', 10)
            if name[8] == 'ute': # sjekker om løperen har kommet i mål
                # Sett fonten til cursiv
                # Fjern nummer, tid og diff
                name[1] =' '
                name[6] = 'Ikke i mål '
                name[7] = ' '
                self.p.setFont('Helvetica-Oblique', 10)
            self.p.drawCentredString(x+10, self.line,  name[1])
            self.p.drawString(x+tab[0], self.line,  name[2])
            self.p.drawString(x+tab[1], self.line,  name[3])
            self.p.drawCentredString(x+tab[2], self.line,  name[6])
            self.p.drawCentredString(x+tab[3], self.line,  name[7])
            self.line = self.line - dy
            i += 1
            if self.line <= 80: # Page Break
                # Sideskift ved full side
                self.p.showPage()
                self.line = 750
                self.print_heading()
                self.print_class_heading()

        #Sideskift når det skal være en side per klasse

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

    # Her må jeg legge inn begge treene!
    def write_result_list(self, class_name):
        # denne kjøres kontinuerlig så og derfor må jeg sette flgg om ikke endrer urangerte lister kontinuerlig. 
        # Her setter jeg randomize lik False
        # Hvis det er H/D -10 eller N-åpen så skal det være urangerte lister
        # skal jeg sjekke her om det er H/D - 10 her?
        self.randomized = False

        if self.class_name:
            self.b.after_cancel(self.btree_alarm)
            self.a.after_cancel(self.atree_alarm)

        out_list = self.update_out_list(class_name)
        self.write_table(out_list,'b')
        self.btree_alarm = self.b.after(200, self.write_result_list, class_name)

# Her legger jeg inn en nu update result list som bare inneholde de som er ute
        result_list = self.update_result_list(class_name)
        self.write_table(result_list,'a')
        self.atree_alarm = self.a.after(250, self.write_result_list, class_name)

        self.class_name = class_name

    def update_result_list(self, class_name):
        urangert = False
        uten_tid = False
        results = []
        vinnertid = None
        result_list = []
        dns = []
        dsq = []
        plass = 0
        #self.db.update_db()
        data = self.race.find_class(class_name)
#        self.b.tree.delete(*self.b.tree.get_children())
        self.a.tree.delete(*self.a.tree.get_children())
        for name in data:
            # sjekker om løperen ikke er kommet i mål.
            name = list(name)
            if not name[8] or name[10] =='I':
                #Regner ut tiden
                name[8] = get_time(name[14])
            #Setter tag
            name[10] = set_tag(name[10])
            results.append(name)
        # sortere rekkefølgen på resultatene
        # Her må jeg ha et flagg som sier at klasser ikke skal sortere lista

        # H 10 og D 10 skal ha urangerte lister, men det kan være med tider
        # N-åpen skal ikke ha tider bare deltatt eller ikke
        # H/D 11-12N kan ha rangerte lister
        
        if (class_name == 'H -10' or class_name == 'D -10' or class_name == 'N-åpen') and self.print_results:
            #print(class_name)
            random.shuffle(results)
            self.print_results = False
            urangert = True

            if (class_name == 'NY' or class_name == 'N-åpen'):
                uten_tid = True


        else:
            #Sorterer listen
            results = sorted(results, key=lambda tup: str(tup[8]))  # , reverse=True)

        # regne ut differanse i forhold til ledertid
        # Finn vinnertiden
        for name in results:
            # Sjekker om løperen ikke er disket eller ikke har startet aller ar arrangør
            if not (name[10] == 'dsq' or name[10] == 'dns' or name[10] == 'arr' or name[10] == 'ute'):
                if not vinnertid:
                    vinnertid = name[8]
                plass += 1
                # Finner differansen
                diff = name[8] - vinnertid
                if not name[14]:
                    name[14] = ' '
                else:
                    name[14] = str(name[14].time())
                if urangert:
                    text = [name[7], str(plass), name[2], name[3], class_name, name[14], str(name[8]),
                    str(''), name[10]]
                    if uten_tid:
                        text = [name[7], str(plass), name[2], name[3], class_name, name[14], str(''),
                        str(''), name[10]]
                else:
                    text = [name[7], str(plass), name[2], name[3], class_name, name[14], str(name[8]),
                    str(diff), name[10]]
                result_list.append(text)
            else: # Disket elle DNS
                if name[10] == 'dsq':
                    text = [name[7], str(' '), name[2], name[3], class_name, str(' '), str('DSQ'), str('-'), name[10]]
                    dsq.append(text)
                if name[10] == 'dns':
                    text = [name[7], str(' '), name[2], name[3], class_name, str(' '), str('DNS'), str('-'), name[10]]
                    dns.append(text)
        #Putter DNS i bunn og DSQ over der
        result_list.extend(dsq)
        result_list.extend(dns)

        return result_list

    def update_out_list(self, class_name):
        results = []
        vinnertid = None
        result_list = []
        dns = []
        dsq = []
        plass = 0
        # self.db.update_db()
        data = self.race.find_class(class_name)
        self.b.tree.delete(*self.b.tree.get_children())
 #       self.a.tree.delete(*self.a.tree.get_children())
        for name in data:
            name = list(name)
            # sjekker om løperen har registrert sluttid
            #if not name[8]:
            if name[10] == 'I':
                # Regner ut tiden
                name[8] = get_time(name[14])
            # Tagger løper om den er inne, ute, dns, dsq eller arr.
            name[10] = set_tag(name[10])
            results.append(name)
        # sortere rekkefølgen på resultatene
        results = sorted(results, key=lambda tup: str(tup[8]))  # , reverse=True)

        # regne ut differenase i forhold til ledertid
        # Finn vinnertiden
        for name in results:
            # Sjekker om løperen ikke er disket, ikke har startet eller er arrangør, eller er inne.
            if  (name[10] == 'ute'):
                if not name[14]:
                    name[14] = ' '
                else:
                    name[14] = str(name[14].time())

                text = [name[7], str(' '), name[2], name[3], class_name, name[14], str(name[8]),
                        str(' '), name[10]]
                result_list.append(text)

        return result_list


    def write_table(self, data, table):
        for name in reversed(data):
            if table == 'a':
                self.a.LoadinTable(name)
            else:
                self.b.LoadinTable(name)

    # Finner løper fra Brikkesys databasen og skriver denne i øverste tabell. Løperne må ha startnummer.
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

    def get_event(self, event):
        #print(self.combo_races.get())
        self.race = Event(self.db, self.combo_races.current())
        #print(self.combo_races.current())
        try:
            if self.button:
                for knapp in self.button:
                    knapp.grid_remove()
        except:
            self.button = list()
        i = 1
        j = 0
        for name in self.race.class_names:
            self.button.append(tk.Button(self.ctr_left, text=name, command=partial(self.write_result_list, name)))
            self.button[-1].grid(row=i, column=j)
            i += 1
            if i >= 30:
                j = 1
                i = 1
        self.window.mainloop()

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


class App(TTK.Frame):

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
        tv.column('klasse', anchor='center', width=100)
        tv.heading('starttid', text='Starttid')
        tv.column('starttid', anchor='center', width=200)
        tv.heading('tid', text='Tid')
        tv.column('tid', anchor='center', width=200)
        tv.heading('diff', text='Differanse')
        tv.column('diff', anchor='center', width=200)
        tv.grid(sticky=('n'))#, 'S', 'W', 'E'))
        return tv

    def LoadTable(self):
        self.tree.insert('', 'end', text="First", values=('10:00', '10:10', 'Ok'))

    #        self.treeview.insert('', 'end', text="First", values=('10:01','10:11', 'Ok'))

    def LoadinTable(self, entry):
       # print(entry)

        # Sjekker om de har startnummer
        if not entry[0]:
            entry[0] = ' '
        self.tree.insert('', 0, text=entry[0], values=(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]), tags = (entry[8],))

    # def tick(self):
    #
    #     s = time.strftime('%H:%M:%S')
    #     curItem = self.tree.item(self.tree.focus())
    #     #col = self.tree.identify_column(event.x)
    #     for item in x:
    #         self.tree.item(item, text='test')
    #
    #     if s != x:
    #         print('hello')
    #     self.after(200, self.tick)



    # def tick(self):
    #     global time1
    #     # get the current local time from the PC
    #     time2 = time.strftime('%H:%M:%S')
    #     # if time string has changed, update it
    #     if time2 != time1:
    #         time1 = time2
    #         clock.config(text=time2)
    #     # calls itself every 200 milliseconds
    #     # to update the time display as needed
    #     # could use >200 ms, but display gets jerky
    #     clock.after(200, tick)


def main():
    #o_event = Event()
    #o_event.get_event(43)
    #o_event.find_names()
    #o_event.get_classes()
    #o_event.print_class(782)

    gui()

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
