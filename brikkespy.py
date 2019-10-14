#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
import ospeakerui as gui

def main():
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', nargs='?', default= 'local', help='Server med brikkesys, local, Klara, Milo eller Prewarn')
    parser.add_argument('os', nargs='?', default='linux', help='Sett win hvis det er windowspc')
    parser.add_argument('ekstra', nargs='?', default='no', help='Sett til forvarsel hvis det skal være forvarsel, poengo hvis det skal være PoengO')
    args = parser.parse_args()
    if args.server:
        res_db = args.server
    else:
        res_db = 'local'
    if args.os:
        os = args.os
    else:
        os = 'linux'
    if args.ekstra == 'forvarsel':
        extra='forvarsel'
    if args.ekstra == 'poengo':
        ekstra = 'poengo'
    else:
        ekstra='no'

    my_app = gui.Window()
    my_app.add_tab(res_db, os, ekstra)
    my_app.add_menu(res_db, os)
    my_app.mainloop()

if __name__=="__main__":
    main()  # Create GUI
