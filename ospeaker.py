#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from functools import partial
import argparse
from brikkesys import Database
from oRace import Race
import ospeakerUI as gui

class Manager:
    def __init__(self,*args,**kwargs):
        db = kwargs['database']
        my_app = gui.Window()
        win_width = my_app.winfo_screenwidth()
        win_height = my_app.winfo_screenheight()
        res= str(win_width)+'x'+str(win_height)
        my_app.geometry(res)
        my_app.configure(background='black')
      # Legger inn administrasjonsfane som har 2 vinduer. En for de som er ute og en for de som er imål
        adm_tab= gui.Tab(my_app.notebook, width=str(win_width), height=str(int((win_height-260)/2)), tab_type='adm', database=db)
        my_app.notebook.add(adm_tab,text='Administrasjon')

        res_tab= gui.Tab(my_app.notebook, width=str(win_width), height=str(int(win_height-250)), tab_type='results', database=db)
        my_app.notebook.add(res_tab,text='Resultater')

        my_app.notebook.grid(row=0)
        my_app.add_menu(db)
        my_app.mainloop()

    def dummy_func(self,event):
        print(event.widget.get())

def main():
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', help='Server med brikkesys, local, Klara, Milo eller Prewarn')
    args = parser.parse_args()
    if args.server:
        res_db = args.server
    else:
        res_db = 'local'
#   log_file = open("/var/log/ospeaker.log", "w")
    pre_db = 'Prewarn'
    coach = Manager(database=res_db)


if __name__=="__main__":
    main()  # Create GUI


