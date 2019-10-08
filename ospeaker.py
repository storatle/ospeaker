#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import tkinter as tk  # Import tKinter
import tkinter.ttk as TTK
from functools import partial
import argparse
from brikkesys import Database
from oRace import Race
import ospeakerUI as gui

                
def main():
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', nargs='?', default= 'local', help='Server med brikkesys, local, Klara, Milo eller Prewarn')
    parser.add_argument('os', nargs='?', default='linux', help='Operation system')
    args = parser.parse_args()
    if args.server:
        res_db = args.server
    else:
        res_db = 'local'
    if args.os:
        os = args.os
    else:
        os = 'win'

    pre_db = 'Prewarn'

    my_app = gui.Window()
    my_app.add_tab(res_db)
    my_app.add_menu(res_db)
    my_app.mainloop()

if __name__=="__main__":
    main()  # Create GUI


