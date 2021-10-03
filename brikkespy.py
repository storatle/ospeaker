#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
import ospeakerui as gui

def main():
    parser = argparse.ArgumentParser(description='Speakermodul for Brikkesys')
    parser.add_argument('server', nargs='?', default='local', help='Server med brikkesys, local, Klara, Milo. ipadresse, brukernavn og passord må være satt i config_brikkesys.py. default=local')
    parser.add_argument('-os', '--opsys', type=str, choices=['linux','windows'], default='linux',help='Setter hvilket opesativssystem som skal benyttes. default=linux')
    parser.add_argument('-f', '--finish', action='store_true', help='Lager liste med de som kommer rett i mål')
    parser.add_argument('-pre', '--prewarn', type=str, help='Sett navn til forvarseldatabasen. Ipadresse, brukernavn og passord må vare satt i config_brikkesys.py')
    parser.add_argument('-p', '--poengo', action='store_true', help='PoengO, poeng og postkoder må settes i config_poengo.py')
    parser.add_argument('-v', '--ovirus', action='store_true', help='O-Virus, poeng og postkoder må settes i config_poengo.py')
    args = parser.parse_args()

    my_app = gui.Window()
    my_app.add_tab(args)
    my_app.add_menu(args)
    my_app.mainloop()

if __name__=="__main__":
    main()  # Create GUI
    

