#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import xml.etree.ElementTree as ET
import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from functools import partial
import os
from PIL import ImageTk, Image
import random
import time
from datetime import datetime, timedelta
import heading
import pdfgen
import argparse
from brikkesys import Database
from oRace import Race
import ospeakerUI as gui

class Manager:
    def __init__(self,*args,**kwargs):
        self.db = Database(kwargs['database'])
        my_app = gui.Window()
        res= str(my_app.winfo_screenwidth())+'x'+str(my_app.winfo_screenheight())
        my_app.geometry(res)
        my_app.configure(background='black')
        self.adm_tab= gui.Tab(my_app.notebook, width=str(my_app.winfo_screenwidth()), height=str(int(my_app.winfo_screenheight())), tab_type='adm')
        my_app.notebook.add(self.adm_tab,text='Administrasjon')
        my_app.notebook.grid(row=0)

        # Combobox med alle løpene i databasen
        tk.Label(self.adm_tab.top_frame, text="Løp:").grid(row=0, column=1, sticky='w')
        # Combobox med alle løp i databasen
        combo_races = TTK.Combobox(self.adm_tab.top_frame, width=30, values=list(zip(*self.db.races))[1])
        combo_races.grid(row=0, column=2, sticky='w')
        combo_races.bind("<<ComboboxSelected>>",self.get_race) 

       # file-Meny 
        menubar = tk.Menu(my_app, bg = "white")
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.dummy_func)#,'Open file....')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=my_app.quit)
          # Lager PDF meny
        pdf_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="PDF", menu=pdf_menu)
        pdf_menu.add_command(label="Lag startliste", command=lambda: pdf_list(False)) #one_active_class, class_name, page_break))
        #pdf_menu.add_command(label="Lag startliste for start", command=lambda: pdf_list(False)) #(self.race, True, self.one_active_class, self.page_break))
        pdf_menu.add_separator()
        pdf_menu.add_command(label="Lag resultatliste", command=lambda: pdf_list(True))#(self.race, self.one_active_class, self.page_break))

       #my_app.notebook.tab(0).page_break
        try:
            my_app.config(menu=menubar)
        except AttributeError:
            print('Error')
        my_app.mainloop()   
        #gui()

    def dummy_func(self,event):
        print(event.widget.get())

# Henter løpene og lager knapper for hver eneste klasse i løpet.
    def get_race(self, event):
        # Henter ønsket løp fra Combobox
        self.race = Race(self.db, event.widget.current())
#        global race_number
#        race_number = self.combo_races.current()
#        # Lager knapper for hver klasse
        try:
           if buttons:
                for button in buttons:
                    button.grid_remove()
        except:
            buttons = list()
        i = 0
        j = 0
        for class_name in self.race.class_names:
            buttons.append(tk.Button(self.adm_tab.ctr_left, text=class_name, command=partial(self.adm_tab.write_result_list, class_name)).grid(row=i,column=j, padx = 10))
            i += 1
            if i >= 30:
                j += 1
                i = 0

def main():
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
    log_file = open("/var/log/ospeaker.log", "w")
    pre_db = 'Prewarn'
    coach = Manager(database=res_db)

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

def get_next_element(my_itr):
    try:
        return next(my_itr)
    except StopIteration:
        return None

if __name__=="__main__":
    main()  # Create GUI


