#!/usr/bin/env python3

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas as cv
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import heading
import os



def demo():
        merger = PdfFileMerger()
        p = cv.Canvas('demo.pdf')
        line = 750
        x = 50
        p.setFont('Helvetica-Bold', 14)
        p.drawString(300, 785, 'MELHUS ORIENTERING')
#        drawing = svg2rlg('Logo MIL vektor.svg')
        drawing = svg2rlg('MIL ny Logo 2019 Sort.svg')
        renderPDF.draw(drawing, p, 110, 250)
        p.setFont('Helvetica-Bold', 12)
        p.save()
        merger.append(PdfFileReader('demo.pdf'))
        merger.write("demo.pdf")
        merger.close()
 ## Printer tittel på PDF-resultatlister
        
demo()
