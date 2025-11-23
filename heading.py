#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Column Heading Configuration Module for BrikkeSpy/OSpeaker

This module provides column heading configurations for different list types
used throughout the application. Each heading configuration defines column
labels and their positions or widths for PDF generation and GUI displays.

Functions:
    get_heading(head): Returns column configuration for specified list type
    line_shift(): Returns empty row template for GUI displays
    class_heading(class_name): Returns class separator row for GUI displays

Heading Types:
    PDF Formats (positions in points from left margin):
        - 'pdf forstart': Pre-start list with OK checkbox column
        - 'pdf start': Standard start list
        - 'pdf result': Result list without points
        - 'pdf result poeng': Result list with points column

    GUI Formats (width ratios and alignment):
        - 'resultater': Standard result display in GUI
        - 'poengo': PoengO scoring display with multiple point columns
"""


def get_heading(head):
    """
    Get column heading configuration for specified list type.

    Returns a dictionary mapping column labels to their positions (for PDF)
    or formatting parameters (for GUI). PDF headings use absolute x-positions
    in points from the left margin. GUI headings use [width_ratio, alignment]
    pairs where width_ratio is fraction of total width.

    Args:
        head (str): Heading type identifier. Valid values:
            - 'pdf forstart': Pre-start list (includes OK checkbox column)
            - 'pdf start': Standard start list
            - 'pdf result': Result list without points
            - 'pdf result poeng': Result list with point scores
            - 'resultater': GUI results treeview
            - 'poengo': GUI PoengO scoring treeview

    Returns:
        dict: Column configuration mapping.
            For PDF types: {label: x_position_in_points}
            For GUI types: {label: [width_ratio, alignment]}

            Alignments: 'w' (west/left), 'center', 'e' (east/right)

    Examples:
        >>> get_heading('pdf start')
        {'Startnr': 20, 'Brikkenr': 60, 'Navn': 120, ...}

        >>> get_heading('resultater')
        {'Plass': [0.07, 'center'], 'Navn': [0.26, 'w'], ...}
    """

    # Pre-start list for race officials
    # Includes OK checkbox column for manual checking before start
    if head == 'pdf forstart':
        return {
            'OK': 0,            # Checkbox column position
            'Startnr': 20,      # Start number
            'Brikkenr': 60,     # E-card number (brikke = chip/card)
            'Navn': 120,        # Runner name
            'Klubb': 300,       # Club name
            'Klasse': 430,      # Class name
            'Starttid': 480     # Start time
        }

    # Standard start list (no checkbox column)
    elif head == 'pdf start':
        return {
            'Startnr': 20,      # Start number
            'Brikkenr': 60,     # E-card number
            'Navn': 120,        # Runner name
            'Klubb': 300,       # Club name
            'Klasse': 400,      # Class name
            'Starttid': 480     # Start time
        }

    # Standard result list (traditional orienteering format)
    elif head == 'pdf result':
        return {
            'Plass': 20,        # Placement/rank
            'Navn': 50,         # Runner name
            'Klubb': 250,       # Club name
            'Tid': 380,         # Finish time
            'Differanse': 430   # Time difference from winner
        }

    # Result list with points (for PoengO, OG-karusell, O-6er formats)
    elif head == 'pdf result poeng':
        return {
            'Plass': 20,        # Placement/rank
            'Navn': 50,         # Runner name
            'Klubb': 250,       # Club name
            'Tid': 380,         # Finish time
            'Differanse': 430,  # Time difference from winner
            'Poeng': 500        # Point score
        }

    # GUI treeview: Standard results display
    # Format: {label: [width_ratio, alignment]}
    # width_ratio: Fraction of total treeview width (sums to ~1.0)
    # alignment: 'w' (left), 'center', 'e' (right)
    elif head == "resultater":
        return {
            'Plass': [0.07, 'center'],       # Placement (7% width, centered)
            'Navn': [0.26, 'w'],             # Name (26% width, left-aligned)
            'Klubb': [0.2, 'w'],             # Club (20% width, left-aligned)
            'Klasse': [0.1, 'center'],       # Class (10% width, centered)
            'Starttid': [0.1, 'center'],     # Start time (10% width, centered)
            'Tid': [0.1, 'center'],          # Finish time (10% width, centered)
            'Differanse': [0.1, 'center']    # Time diff (10% width, centered)
        }

    # GUI treeview: PoengO scoring display
    # Shows multiple point categories and penalties for point orienteering
    elif head == "poengo":
        return {
            'Plass': [0.05, 'center'],         # Placement (5% width)
            'Navn': [0.2, 'w'],                # Name (20% width)
            # 'Klubb': [0.18, 'w'],            # Club - commented out to save space
            'Tid': [0.08, 'center'],           # Finish time
            'Sprint': [0.08, 'center'],        # Sprint lap time/points
            'Klatrestrekk': [0.08, 'center'],  # Climb lap time/points
            'Postpoeng': [0.07, 'center'],     # Control point scores
            'Strekkpoeng': [0.07, 'center'],   # Bonus track scores
            # 'Vaksinepoeng': [0.08, 'center'], # Vaccine points - deprecated
            'Bonuspoeng': [0.07, 'center'],    # Age class bonus points
            'Ekstrapoeng': [0.07, 'center'],   # Extra/special points
            'Tidstraff': [0.07, 'center'],     # Time penalty (negative points)
            'Poengsum': [0.07, 'center']       # Total point score
        }


def line_shift():
    """
    Generate empty row template for GUI displays.

    Creates a dictionary with all possible column keys mapped to empty strings.
    Used for inserting blank separator rows between sections in treeview displays.

    Returns:
        dict: All column keys mapped to empty strings

    Usage:
        Used in GUI to create visual spacing between classes or sections:
        >>> empty_row = line_shift()
        >>> treeview.insert('', 'end', values=empty_row)
    """
    return {
        'Startnr': str(''),      # Start number
        'Plass': str(''),        # Placement
        'Navn': str(''),         # Name
        'Klubb': str(''),        # Club
        'Tid': str(''),          # Time
        'Differanse': str(''),   # Time difference
        'Klasse': str(''),       # Class
        'Starttid': str(''),     # Start time
        'tag': str(''),          # Row tag for styling
        'Brikkenr': str(''),     # E-card number
        'Poeng': str('')         # Points
    }


def class_heading(class_name):
    """
    Generate class separator heading row for GUI displays.

    Creates a formatted row that displays "Klasse: [name]" in the Name column,
    with all other columns empty. Used to visually separate different classes
    in continuous result displays. The 'tag' field is set to 'title' to enable
    special formatting (e.g., bold, colored background) in the GUI.

    Args:
        class_name (str): Name of the class to display

    Returns:
        dict: Row data with class name in 'Navn' field and 'title' tag

    Usage:
        Used in GUI to insert class headers in result displays:
        >>> header = class_heading('H 21-39')
        >>> treeview.insert('', 'end', values=header, tags='title')

    Note:
        The 'tag' value of 'title' should be configured in the GUI to apply
        special formatting (bold font, background color, etc.)
    """
    return {
        'Startnr': str(''),                      # Empty
        'Plass': str(''),                        # Empty
        'Navn': str('Klasse: ') + class_name,    # "Klasse: [name]"
        'Klubb': str(''),                        # Empty
        'Tid': str(''),                          # Empty
        'Differanse': str(''),                   # Empty
        'Klasse': str(''),                       # Empty
        'Starttid': str(''),                     # Empty
        'tag': str('title'),                     # Special formatting tag
        'Brikkenr': str(''),                     # Empty
        'Poeng': str('')                         # Empty
    }
