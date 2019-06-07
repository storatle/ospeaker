#!/usr/bin/env python

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas as cv
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import heading
import os

class Pdf:

    def __init__(self):
        # Denne må flyttes eller så må navnet på fila være en variabel
        self.line = 750

    def start_list(self, race, for_start, one_active_class, class_name, page_break):
        self.startlist = True # Denne brukes i set_class
        self.class_name = class_name
        self.for_start = for_start
        self.page_break = page_break
        self.one_active_class = one_active_class
        self.merger = PdfFileMerger()
        self.p = cv.Canvas('start.pdf')
        self.race_name = race.race_name
        dy = 15
        start_list=[]
        self.set_heading()

        #Sjekker om det er spesialliste for startere
        if self.for_start: 

            # Henter heading og setter tab
            head = heading.get_heading(1)
            tabs = heading.get_heading(1)
            tabs.pop('OK')

            # Lager startliste med alle løpere
            if self.one_active_class: 
                start_list = race.make_start_list(class_name) #one_class = [(0, 'N-åpen')]
            else:
                start_list = race.make_start_list('all')
            if start_list:  # Sjekker om det er deltaker i klassen
                self.active_class = start_list[0][4]
                # Dette er felles for alle lister med følgende input. "Heading, tab, filnavn
                self.make_list(start_list, head, tabs, 'start.pdf')

        else:
            head = heading.get_heading(2)
            tabs = head
            if self.one_active_class: #.get()
                race_classes = class_name
            else:
                race_classes = race.classes
            for race_class in race_classes:
                # Henter resultatliste for klassen
                start_list = race.make_start_list(race_class[1])
                if start_list:  # Sjekker om det er deltaker i klassen
                    self.active_class = start_list[0][4]
                    self.make_list(start_list, head, tabs, 'start.pdf')
        self.p.save()
        self.merger.append(PdfFileReader('start.pdf'))
        self.merger.write("start.pdf")
        #self.merger.close()


    def result_list(self, race, one_active_class, class_name, page_break):
        self.startlist = False
        self.for_start = False
        self.one_active_class = one_active_class
        self.class_name = class_name
        self.page_break = page_break
        self.merger = PdfFileMerger()
        self.p = cv.Canvas('result.pdf')
        self.race_name = race.race_name
        head = heading.get_heading(3)
        tabs = head
        self.line = 750
        self.set_heading()
        if self.one_active_class:
            #one_class = [(0, 'N-åpen')] # Denne skal velge den klassen som jeg har valgt i gui.
            race_classes = self.class_name #one_class = [(0, 'N-åpen')]
        else:
            race_classes = race.classes
        for race_class in race_classes:
            # Henter resultatliste for klassen
            result_list = race.make_result_list(race_class[1])
            if result_list: # Sjekker om det er deltaker i klassen
                self.active_class = race_class[1]
                self.make_list(result_list, head, tabs, 'result.pdf') # Filnavn bør være en variabel
        self.p.save()
        self.merger.append(PdfFileReader('result.pdf'))
        self.merger.write("result.pdf")
        #self.merger.close()

    #Denne funksjonen lager liste denne skal brukes på all utskrifter
    def make_list(self, list, heading, tab, filename):
        if self.page_break: 
            self.set_class_heading(heading)
            self.set_class(list, tab)
            self.p.save()
            self.merger.append(PdfFileReader(filename))
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
                #self.line = self.line - 1.5 * dy
                self.set_class(list, tab)
            else:
                # Hvis det ikke er plass så lages det en ny side
                self.p.showPage()
                self.line = 750
                self.set_heading()
                #self.line = self.line - 1.5 * dy
                self.set_class_heading(heading)
                self.set_class(list, tab)

    ## Printer tittel på PDF-resultatlister
    def set_heading(self):
        x = 50
        self.p.setFont('Helvetica-Bold', 14)
        self.p.drawString(300, 785, 'MELHUS ORIENTERING')
        drawing = svg2rlg('Logo MIL vektor.svg')
        renderPDF.draw(drawing, self.p, 110, 250)
        self.p.setFont('Helvetica-Bold', 12)
        self.p.drawString(x, 785, (self.race_name))

    ## Printer tittel på hver klasse og ved eventuelt sideskifte
    def set_class_heading(self,heading):
        self.line = self.line - 20
        x = 35
        dy = 18
        # Skriver tittel for hver klasse, hvis det ikke skal være spesialliste for startere
        # Kan denne taes utenfor
        if not self.for_start: #.get():
            self.p.setFont('Helvetica-Bold', 12)
            self.p.drawString(x, self.line, 'Klasse:')
            self.p.drawString(x + 55, self.line, self.active_class)
        self.line = self.line - 20

        self.p.setFont('Helvetica-Bold', 10)

        i = 0
        for item in heading.keys():
            self.p.drawString(x + heading.get(item),self.line, item)
            i += 1
        self.line = self.line - 20

    ## Printer PDFstartlister for en klasse
    def set_class(self, list, heading):
        dy = 15
        x = 35
        i = 0
        # Bruker denne for å fjerne 'OK' Tab når jeg skriver til startliste for startere
        excludes = set([])
        start_tid = list[0][5]
        for name in list:
            #print(len(name)):

            self.p.setFont('Helvetica', 10)
            # Skrive ut spesialliste for liste som skal være før start
            if self.for_start:

                # Skriver inn en linje for neste tidsstep
                # Jeg har fortsatt ikke kontroll på avstand mellom linjer og tekst
                # Jeg må også sjekke at det blir sideskift hvis det ikke er nok plass/
                # til et tidsstep.
                if not (start_tid == name['Starttid']):
                    self.p.line(x, self.line+5, 550, self.line)
                    self.line = self.line - 27
                    start_tid = name['Starttid']
                    # Fjerner Tab for OK
                    excludes = set(['OK'])
                self.p.rect(x, self.line, 9, 9)
                dy = 27
                
                # Denne er vel felles for alle lister
            for head in set(heading).differences(excludes):
                self.p.drawString(x + heading[head], self.line, name[head])
                self.line = self.line - dy

            if self.line <= 80:  # Page Break
                # Sideskift ved full side
                self.p.showPage()
                self.line = 750
                self.set_heading()
                self.set_class_heading(heading.get_heading(1))
