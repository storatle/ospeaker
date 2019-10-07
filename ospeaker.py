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
        my_app.add_tab(db)
        my_app.add_menu(db)
        my_app.mainloop()
        
def main():
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', help='Server med brikkesys, local, Klara, Milo eller Prewarn')
    args = parser.parse_args()
    if args.server:
        res_db = args.server
    else:
        res_db = 'local'
    pre_db = 'Prewarn'
    coach = Manager(database=res_db)

if __name__=="__main__":
    main()  # Create GUI


