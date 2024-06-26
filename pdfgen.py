#!/usr/bin/env python

from PyPDF2 import PdfReader, PdfMerger
from reportlab.pdfgen import canvas as cv
import heading
import os
import sys
import subprocess

class Pdf:
    def __init__(self):
        self.line = 750

    def start_list(self, race, for_start, one_active_class, class_name, page_break):
        self.startlist = True # Denne brukes i set_class
        self.class_name = class_name
        self.for_start = for_start
        self.page_break = page_break
        self.one_active_class = one_active_class
        self.merger = PdfMerger()
        self.p = cv.Canvas('startliste.pdf')
        self.race_name = race.race_name
        self.line = 750
        self.set_heading()
        for_list = []

        #Sjekker om det er spesialliste for startere
        if self.for_start: 
            # Henter heading og setter tab
            head = heading.get_heading('pdf forstart')
            # Lager startliste med alle løpere
            if self.one_active_class: 
                start_list = race.make_start_list(class_name) #one_class = [(0, 'N-åpen')]
            else:
                start_list = race.make_start_list('all')
            if start_list:  # Sjekker om det er deltaker i klassen
                self.active_class = start_list[0]['Klasse']
                # Dette er felles for alle lister med følgende input. "Heading, tab, filnavn
                starttid = start_list[0]['Starttid']
                for start in start_list:
                    if start['Starttid'] == starttid:
                        for_list.append(start)
                    else:
                        self.make_list(for_list, head, 'startliste.pdf')
                        for_list = []
                        for_list.append(start)
                        starttid = start['Starttid']

        else:
            head = heading.get_heading('pdf start')
            if self.one_active_class: #.get()
                race_classes = [[0,class_name]]
            else:
                race_classes = race.classes
            for race_class in race_classes:
                # Henter resultatliste for klassen
                start_list = race.make_start_list(race_class[1])
                if start_list:  # Sjekker om det er deltaker i klassen
                    self.active_class = start_list[0]['Klasse']
                    self.make_list(start_list, head, 'startliste.pdf')
        self.p.save()
        self.merger.append(PdfReader('startliste.pdf'))
        self.merger.write("startliste.pdf")
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", "startliste.pdf"])
        else:
            subprocess.call(["evince", "startliste.pdf"])


    def result_list(self, race, one_active_class, class_name, page_break, points):
        self.startlist = False
        self.for_start = False
        self.one_active_class = one_active_class
        self.class_name = class_name
        self.page_break = page_break
        self.merger = PdfMerger()
        self.p = cv.Canvas('resultatliste.pdf')
        self.race_name = race.race_name
        if points:
            head = heading.get_heading('pdf result poeng') # Her må jeg endre til variabel slik at man endre med og ute poeng
        else:
            head = heading.get_heading('pdf result') # Her må jeg endre til variabel slik at man endre med og ute poeng
        self.line = 750
        self.set_heading()
        if self.one_active_class:
            #one_class = [(0, 'N-åpen')] # Denne skal velge den klassen som jeg har valgt i gui.
            race_classes = [[0,self.class_name]] #one_class = [(0, 'N-åpen')]
        else:
            race_classes = race.classes
        for race_class in race_classes:
            # Henter resultatliste for klassen
            result_list = race.make_result_list(race_class[1])
            if result_list: # Sjekker om det er deltaker i klassen
                self.active_class = race_class[1]
                self.make_list(result_list, head, 'resultatliste.pdf') # Filnavn bør være en variabel
        self.p.save()
        self.merger.append(PdfReader('resultatliste.pdf'))
        self.merger.write("resultatliste.pdf")
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", "resultatliste.pdf"])
        else:
            subprocess.call(["evince", "resultatliste.pdf"])


    #Denne funksjonen lager liste denne skal brukes på all utskrifter
    def make_list(self, list, heading, filename):
        if self.page_break: 
            self.set_class_heading(heading)
            self.set_class(list, heading)
            self.p.save()
            self.merger.append(PdfReader(filename))
            os.remove(filename)
            self.p = cv.Canvas(filename)
            self.line = 750
            self.set_heading()
        else:
            #Hvis det er en kjempestor klasse som skal printes over flere sider. /
            #Sjekker lengden på en full klasse.
            if (self.line - len(
                    list) * 15 - 145) >= 0 or self.line > 600:  # Sjekk om det er plass til en /
                #klasse på resten av siden.
                self.set_class_heading(heading)
                self.set_class(list, heading)
            else:
                # Hvis det ikke er plass så lages det en ny side
                self.p.showPage()
                self.line = 750
                self.set_heading()
                self.set_class_heading(heading)
                self.set_class(list, heading)

    ## Printer tittel på PDF-resultatlister
    def set_heading(self):
        x = 50
        if sys.platform == "win32":
            self.p.drawInlineImage('C:\Program Files (x86)\Brikkespy\images\\white_MILO_banner.png', 0, 10, 600, 85)
        else:
            self.p.drawInlineImage('/etc/white_MILO_banner.png', 0, 10, 600, 85)
        self.p.setFont('Helvetica-Bold', 12)
        self.p.drawString(x, 785, (self.race_name))

    ## Printer tittel på hver klasse og ved eventuelt sideskifte
    def set_class_heading(self,heading):
        self.line = self.line - 20
        x = 35
        dy = 18
        # Skriver tittel for hver klasse, hvis det ikke skal være spesialliste for startere
        if not self.for_start: #.get():
            self.p.setFont('Helvetica-Bold', 12)
            self.p.drawString(x, self.line, 'Klasse:')
            self.p.drawString(x + 55, self.line, self.active_class)
        self.line = self.line - 20

        self.p.setFont('Helvetica-Bold', 10)
        for item in heading.keys():
            self.p.drawString(x + heading.get(item),self.line, item)
        self.line = self.line - 20

    ## Printer PDFstartlister for en klasse
    def set_class(self, list, heading):
        dy = 15
        x = 35
        # Bruker denne for å fjerne 'OK' Tab når jeg skriver til startliste for startere
        excludes = set([])
        start_tid = list[0]['Starttid']
        for name in list:
            self.p.setFont('Helvetica', 10)
            # Skrive ut spesialliste for liste som skal være før start
            if self.for_start:
                excludes = set(['OK'])
                # Skriver inn en linje for neste tidsstep
                # Jeg har fortsatt ikke kontroll på avstand mellom linjer og tekst
                # Jeg må også sjekke at det blir sideskift hvis det ikke er nok plass/
                # til et tidsstep.
                if not (start_tid == name['Starttid']):
                    self.p.line(x, self.line+5, 550, self.line)
                    self.line = self.line - 27
                    start_tid = name['Starttid']
                    # Fjerner Tab for OK
                self.p.rect(x, self.line, 9, 9)
                dy = 27
                # Denne er vel felles for alle lister
            for head in set(heading).difference(excludes):
                self.p.drawString(x + heading[head], self.line, name[head])
            self.line = self.line - dy

            if self.line <= 80:  # Page Break
                # Sideskift ved full side
                self.p.showPage()
                self.line = 750
                self.set_heading()
                self.set_class_heading(heading)
