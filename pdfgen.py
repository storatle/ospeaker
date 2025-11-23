#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Generation Module for BrikkeSpy/OSpeaker

This module generates professional PDF start lists and result lists for
orienteering races using ReportLab and PyPDF2. Supports page breaks,
class-specific formatting, and pre-start special lists.

Classes:
    Pdf: Main PDF generator with methods for start lists and result lists
"""

from PyPDF2 import PdfReader, PdfMerger
from reportlab.pdfgen import canvas as cv
import heading
import os
import sys
import subprocess


# PDF Layout Constants
PAGE_TOP_MARGIN = 750      # Starting Y position for content
PAGE_BOTTOM_MARGIN = 80    # Minimum Y before page break
LINE_SPACING = 15          # Standard line height
HEADER_LINE_SPACING = 20   # Line height for headers
PRESTART_LINE_SPACING = 27 # Line height for pre-start lists with checkboxes
CLASS_THRESHOLD = 600      # Minimum space needed for new class


class Pdf:
    """
    PDF generator for orienteering race start lists and result lists.

    Generates formatted PDFs with race branding, automatic page breaks,
    and support for different list types (start, result, pre-start).

    Attributes:
        line (int): Current Y-position for text rendering
        race_name (str): Name of the race being printed
        p (Canvas): ReportLab canvas object for PDF generation
        merger (PdfMerger): PyPDF2 merger for combining PDF pages
        active_class (str): Currently active class being printed
        startlist (bool): Flag indicating if generating start list
        for_start (bool): Flag for pre-start special format
        page_break (bool): Whether to force page break between classes
        one_active_class (bool): Whether printing single class or all
        class_name (str): Name of specific class (if one_active_class=True)
    """

    def __init__(self):
        """Initialize PDF generator with default line position."""
        self.line = PAGE_TOP_MARGIN

    def start_list(self, race, for_start, one_active_class, class_name, page_break):
        """
        Generate PDF start list for orienteering race.

        Creates formatted start list with runner names, start times, and classes.
        Can generate for all classes or a single class, with optional page breaks
        between classes. Special 'for_start' mode groups runners by start time
        with checkboxes for race officials.

        Args:
            race (Race): Race object containing runner and class data
            for_start (bool): If True, generates special pre-start format grouped
                            by start time with checkboxes (for race officials)
            one_active_class (bool): If True, generates list for single class only
            class_name (str): Name of class to print (used if one_active_class=True)
            page_break (bool): If True, starts each class on new page

        Side Effects:
            - Creates 'startliste.pdf' in current directory
            - Opens PDF in system viewer (Explorer on Windows, Evince on Linux)
        """
        # Initialize list configuration
        self.startlist = True  # Used in set_class method
        self.class_name = class_name
        self.for_start = for_start
        self.page_break = page_break
        self.one_active_class = one_active_class

        # Setup PDF generation objects
        self.merger = PdfMerger()
        self.p = cv.Canvas('startliste.pdf')
        self.race_name = race.race_name
        self.line = PAGE_TOP_MARGIN
        self.set_heading()

        # List to accumulate runners for current group
        for_list = []

        # Special pre-start format: Group runners by start time with checkboxes
        if self.for_start:
            # Get heading configuration for pre-start format
            head = heading.get_heading('pdf forstart')

            # Generate start list (single class or all classes)
            if self.one_active_class:
                start_list = race.make_start_list(class_name)
            else:
                start_list = race.make_start_list('all')

            if start_list:  # Check if there are any participants
                self.active_class = start_list[0]['Klasse']

                # Group runners by start time and create separate sections
                starttid = start_list[0]['Starttid']
                for start in start_list:
                    if start['Starttid'] == starttid:
                        # Same start time - add to current group
                        for_list.append(start)
                    else:
                        # New start time - print current group and start new one
                        self.make_list(for_list, head, 'startliste.pdf')
                        for_list = []
                        for_list.append(start)
                        starttid = start['Starttid']

        # Standard start list format: Organized by class
        else:
            head = heading.get_heading('pdf start')

            # Determine which classes to print
            if self.one_active_class:
                race_classes = [[0, class_name]]
            else:
                race_classes = race.classes

            # Generate start list for each class
            for race_class in race_classes:
                start_list = race.make_start_list(race_class[1])
                if start_list:  # Check if class has participants
                    self.active_class = start_list[0]['Klasse']
                    self.make_list(start_list, head, 'startliste.pdf')

        # Finalize PDF and open in viewer
        self.p.save()
        self.merger.append(PdfReader('startliste.pdf'))
        self.merger.write("startliste.pdf")

        # Open PDF in platform-specific viewer
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", "startliste.pdf"])
        else:
            subprocess.call(["evince", "startliste.pdf"])


    def result_list(self, race, one_active_class, class_name, page_break, points):
        """
        Generate PDF result list for orienteering race.

        Creates formatted result list with placements, times, and optionally
        point scores for PoengO races. Supports single class or all classes
        with optional page breaks.

        Args:
            race (Race): Race object containing results data
            one_active_class (bool): If True, generates list for single class only
            class_name (str): Name of class to print (used if one_active_class=True)
            page_break (bool): If True, starts each class on new page
            points (bool): If True, includes point scores (PoengO format)

        Side Effects:
            - Creates 'resultatliste.pdf' in current directory
            - Opens PDF in system viewer (Explorer on Windows, Evince on Linux)
        """
        # Initialize list configuration
        self.startlist = False
        self.for_start = False
        self.one_active_class = one_active_class
        self.class_name = class_name
        self.page_break = page_break

        # Setup PDF generation objects
        self.merger = PdfMerger()
        self.p = cv.Canvas('resultatliste.pdf')
        self.race_name = race.race_name

        # Select heading format based on points flag
        if points:
            head = heading.get_heading('pdf result poeng')
        else:
            head = heading.get_heading('pdf result')

        # Initialize page and heading
        self.line = PAGE_TOP_MARGIN
        self.set_heading()

        # Determine which classes to print
        if self.one_active_class:
            race_classes = [[0, self.class_name]]
        else:
            race_classes = race.classes

        # Generate result list for each class
        for race_class in race_classes:
            result_list = race.make_result_list(race_class[1])
            if result_list:  # Check if class has participants
                self.active_class = race_class[1]
                self.make_list(result_list, head, 'resultatliste.pdf')

        # Finalize PDF and open in viewer
        self.p.save()
        self.merger.append(PdfReader('resultatliste.pdf'))
        self.merger.write("resultatliste.pdf")

        # Open PDF in platform-specific viewer
        if sys.platform == "win32":
            subprocess.call(["explorer.exe", "resultatliste.pdf"])
        else:
            subprocess.call(["evince", "resultatliste.pdf"])


    def make_list(self, list, heading, filename):
        """
        Render a list (start or result) onto PDF canvas with pagination.

        Handles automatic page breaks, class headers, and spacing. Can either
        force page break between classes or flow classes continuously.

        Args:
            list (list): List of runner dictionaries to print
            heading (dict): Column heading configuration {label: x_position}
            filename (str): PDF filename for saving/merging

        Logic:
            - If page_break=True: Always starts class on new page
            - If page_break=False: Checks if class fits on current page,
              creates new page only if needed
        """
        if self.page_break:
            # Force page break: Start each class on new page
            self.set_class_heading(heading)
            self.set_class(list, heading)

            # Save current page and merge into main PDF
            self.p.save()
            self.merger.append(PdfReader(filename))
            os.remove(filename)

            # Create new page
            self.p = cv.Canvas(filename)
            self.line = PAGE_TOP_MARGIN
            self.set_heading()
        else:
            # Continuous flow: Only break page if class doesn't fit
            # Calculate space needed: class lines + header space
            space_needed = len(list) * LINE_SPACING + 145
            space_available = self.line - PAGE_BOTTOM_MARGIN

            # Check if class fits on current page, or if page still mostly empty
            if space_available >= space_needed or self.line > CLASS_THRESHOLD:
                # Class fits - print on current page
                self.set_class_heading(heading)
                self.set_class(list, heading)
            else:
                # Class doesn't fit - start new page
                self.p.showPage()
                self.line = PAGE_TOP_MARGIN
                self.set_heading()
                self.set_class_heading(heading)
                self.set_class(list, heading)


    def set_heading(self):
        """
        Print main page heading with race name and banner.

        Displays MILO banner image and race name at top of each page.
        Banner path differs between Windows and Linux.

        Side Effects:
            - Draws banner image at bottom of page (for letterhead effect)
            - Draws race name at top of page in bold
        """
        x = 50

        # Load platform-specific banner image
        if sys.platform == "win32":
            banner_path = r'C:\Program Files (x86)\Brikkespy\images\white_MILO_banner.png'
        else:
            banner_path = '/etc/white_MILO_banner.png'

        # Draw banner at bottom of page (letterhead style)
        self.p.drawInlineImage(banner_path, 0, 10, 600, 85)

        # Draw race name at top
        self.p.setFont('Helvetica-Bold', 12)
        self.p.drawString(x, 785, self.race_name)


    def set_class_heading(self, heading):
        """
        Print class name and column headings.

        Displays class name (unless in pre-start mode) followed by column
        headers for the table.

        Args:
            heading (dict): Column heading configuration {label: x_position}

        Side Effects:
            - Advances self.line position downward
            - Prints "Klasse: [name]" and column headers
        """
        self.line = self.line - HEADER_LINE_SPACING
        x = 35

        # Print class name (skip for pre-start special format)
        if not self.for_start:
            self.p.setFont('Helvetica-Bold', 12)
            self.p.drawString(x, self.line, 'Klasse:')
            self.p.drawString(x + 55, self.line, self.active_class)

        self.line = self.line - HEADER_LINE_SPACING

        # Print column headers
        self.p.setFont('Helvetica-Bold', 10)
        for item in heading.keys():
            self.p.drawString(x + heading.get(item), self.line, item)

        self.line = self.line - HEADER_LINE_SPACING


    def set_class(self, list, heading):
        """
        Print all runners for a class with proper formatting.

        Renders each runner's data in table format. For pre-start lists,
        adds checkboxes and horizontal dividers between start time groups.
        Handles automatic page breaks when page fills up.

        Args:
            list (list): List of runner dictionaries
            heading (dict): Column heading configuration {label: x_position}

        Side Effects:
            - Advances self.line position for each runner
            - Creates new pages automatically when needed
            - Draws checkboxes and dividers for pre-start format
        """
        dy = LINE_SPACING  # Default line spacing
        x = 35

        # Track start time for pre-start format dividers
        excludes = set([])
        start_tid = list[0]['Starttid']

        for name in list:
            self.p.setFont('Helvetica', 10)

            # Special formatting for pre-start lists
            if self.for_start:
                # Exclude 'OK' column from pre-start lists
                excludes = set(['OK'])

                # Draw divider line when start time changes
                if not (start_tid == name['Starttid']):
                    self.p.line(x, self.line + 5, 550, self.line)
                    self.line = self.line - PRESTART_LINE_SPACING
                    start_tid = name['Starttid']

                # Draw checkbox for manual checking
                self.p.rect(x, self.line, 9, 9)
                dy = PRESTART_LINE_SPACING

            # Print runner data in columns (skip excluded columns)
            for head in set(heading).difference(excludes):
                self.p.drawString(x + heading[head], self.line, name[head])

            self.line = self.line - dy

            # Automatic page break when reaching bottom margin
            if self.line <= PAGE_BOTTOM_MARGIN:
                self.p.showPage()
                self.line = PAGE_TOP_MARGIN
                self.set_heading()
                self.set_class_heading(heading)
