#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from functools import partial
import pdfgen
import argparse
from brikkesys import Database
from oRace import Race
import ospeakerUI as gui

class Manager:
    def __init__(self,*args,**kwargs):
        self.db = kwargs['database']
        my_app = gui.Window()
        win_width = my_app.winfo_screenwidth()
        win_height = my_app.winfo_screenheight()
        res= str(win_width)+'x'+str(win_height)
        print(res)
        my_app.geometry(res)
        my_app.configure(background='black')
        # Legger inn administrasjonsfane som har 2 vinduer. En for de som er ute og en for de som er imål

        self.adm_tab= gui.Tab(my_app.notebook, width=str(win_width), height=str(int((win_height-260)/2)), tab_type='adm', database='self.db') # NB Databasenavn skal være input ikke hele databasen
        my_app.notebook.add(self.adm_tab,text='Administrasjon')

        self.res_tab= gui.Tab(my_app.notebook, width=str(win_width), height=str(int(win_height-250)), tab_type='results', database='self.db')
        my_app.notebook.add(self.res_tab,text='Resultater')

        my_app.notebook.grid(row=0)
        my_app.add_menu()
        my_app.mainloop()
        #gui()

    def dummy_func(self,event):
        print(event.widget.get())

def main():
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', help='Server med brikkesys, local, Klara, Milo eller Prewarn')
    args = parser.parse_args()
 #   global active_class
 #   global res_db
 #   global pre_db
 #   global log_file
 #
    if args.server:
        res_db = args.server
    else:
        res_db = 'local'
    log_file = open("/var/log/ospeaker.log", "w")
    pre_db = 'Prewarn'
    coach = Manager(database=res_db)

def dummy_func(self, name):
    print(name)

def get_next_element(my_itr):
    try:
        return next(my_itr)
    except StopIteration:
        return None

if __name__=="__main__":
    main()  # Create GUI


