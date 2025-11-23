#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ospeakerui.py - Main GUI application for BrikkeSpy/OSpeaker

This module implements the Tkinter-based graphical user interface for the
orienteering race speaker system. It provides real-time display of race results,
runner status, prewarn notifications, and PoengO scoring.

Architecture:
- Window class: Main application window with menu bar and tabs
- Tab class: Individual tab content for different display modes
- Table class: Reusable treeview component for displaying runner data

Tab Types:
- 'adm': Administration view (split: finished runners / runners still out)
- 'results': Three display modes (klassevis/loop/siste)
- 'prewarn': Online control prewarn system
- 'poengo': PoengO scoring and results
- 'finish': Chronological finish list across all classes

Auto-refresh:
- Uses Tkinter .after() callbacks to periodically update displays
- Refresh rates: 500ms-5000ms depending on tab type
- Boolean flags control which displays are active
"""

import xml.etree.ElementTree as ET
import tkinter as tk
import tkinter.ttk as TTK
from functools import partial
from brikkesys import Database
import pdfgen
import xmlgen
import csv
from PIL import ImageTk, Image
import heading as hdn
from orace import Race
import sys
import screeninfo


class Window(tk.Tk):
    """
    Main application window for OSpeaker.

    Creates the main window with:
    - Notebook widget for tabs
    - Menu bar (File, PDF, XML)
    - Screen size detection for full-screen display
    - Global configuration variables for PDF generation

    The window automatically sizes to the current monitor and provides
    a black background for speaker display visibility.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize main application window.

        Sets up:
        - Tkinter notebook for tabs
        - Screen resolution detection
        - Global PDF configuration variables
        - Black background for speaker display
        """
        tk.Tk.__init__(self, *args, **kwargs)
        self.notebook = TTK.Notebook()

        # PDF generation configuration (shared across menus)
        # Note: These are intentionally global to allow access from menu callbacks
        global page_break, one_active_class, for_start, with_points
        global active_class, race_number

        active_class = 0
        race_number = 0

        # Tkinter boolean variables for PDF export checkboxes
        page_break = tk.BooleanVar()        # Insert page breaks between classes
        one_active_class = tk.BooleanVar()  # Export only active class
        for_start = tk.BooleanVar()         # Generate start lists
        with_points = tk.BooleanVar()       # Include points in results

        # Detect monitor size and set window to full screen
        current_screen = self.get_monitor_from_coord(self.winfo_x(), self.winfo_y())
        self.win_width = current_screen.width
        self.win_height = current_screen.height
        res = str(self.win_width) + 'x' + str(self.win_height)
        print('resolution: {}'.format(res))
        self.geometry(res)

        # Black background for speaker display visibility
        self.configure(background='black')

    def get_monitor_from_coord(self, x, y):
        """
        Identify which monitor contains the given coordinates.

        Used to ensure the window opens on the correct monitor in
        multi-monitor setups (common for race speaker displays).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Monitor object containing the coordinates, or primary monitor
        """
        monitors = screeninfo.get_monitors()

        # Check monitors in reverse order (handles overlapping edge cases)
        for m in reversed(monitors):
            if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
                return m
        # Default to primary monitor if no match
        return monitors[0]

    def add_tab(self, args):
        """
        Create and add all requested tabs to the notebook.

        Tabs are created based on command-line arguments:
        - 'adm': Always created (administration view)
        - 'results': Always created (result display)
        - 'prewarn': Created if --prewarn flag set
        - 'poengo': Created if --poengo flag set
        - 'finish': Created if --finish flag set

        Args:
            args: Argparse namespace with server and feature flags
        """
        # Administration tab (always present)
        # Split view: finished runners (top) / runners still out (bottom)
        adm_tab = Tab(
            self.notebook,
            width=str(self.win_width),
            height=str(int((self.win_height - 250) / 2)),
            tab_type='adm',
            database=args.server
        )
        self.notebook.add(adm_tab, text='Administrasjon')

        # Results tab (always present)
        # Three display modes: klassevis/loop/siste
        res_tab = Tab(
            self.notebook,
            width=str(self.win_width),
            height=str(int(self.win_height - 250)),
            tab_type='results',
            database=args.server
        )
        self.notebook.add(res_tab, text='Resultater')

        # Prewarn tab (optional)
        # Shows runners who have punched online controls
        if args.prewarn:
            pre_tab = Tab(
                self.notebook,
                width=str(self.win_width),
                height=str(int(self.win_height - 250)),
                tab_type='prewarn',
                database=args.server
            )
            self.notebook.add(pre_tab, text='forvarsel')

        # PoengO scoring tab (optional)
        # Shows point orienteering results with bonus tracks
        if args.poengo:
            poengo_tab = Tab(
                self.notebook,
                width=str(self.win_width),
                height=str(int(self.win_height - 250)),
                tab_type='poengo',
                database=args.server
            )
            self.notebook.add(poengo_tab, text='Poeng-O')

        # Finish list tab (optional)
        # Chronological list of all finishers
        if args.finish:
            finish_tab = Tab(
                self.notebook,
                width=str(self.win_width),
                height=str(int(self.win_height - 250)),
                tab_type='finish',
                database=args.server
            )
            self.notebook.add(finish_tab, text='Målliste')

        # Position notebook in window
        self.notebook.grid(row=0)

    def add_menu(self, args):
        """
        Create and attach menu bar to window.

        Menus:
        - File: Status check (99-codes), Exit
        - PDF: Generate start lists or result lists
        - XML: Export IOF XML 3.0 results

        Args:
            args: Argparse namespace with server configuration
        """
        # Connect to database for menu operations
        self.db = Database(args.server)

        # Create menu bar
        menubar = tk.Menu(self, bg="white")

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        # Status: Check for control unit failures (99-codes)
        file_menu.add_command(label="Status", command=self.find_99ers)
        file_menu.add_command(label="Exit", command=self.quit)

        # PDF menu
        pdf_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="PDF", menu=pdf_menu)
        # Generate PDF start lists
        pdf_menu.add_command(label="Lag startliste", command=lambda: self.pdf_list(False))
        pdf_menu.add_separator()
        # Generate PDF result lists
        pdf_menu.add_command(label="Lag resultatliste", command=lambda: self.pdf_list(True))

        # XML menu
        xml_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="XML", menu=xml_menu)
        # Export IOF XML 3.0 format results
        xml_menu.add_command(label="Lag resultatliste", command=lambda: self.xml_list())

        # Attach menu bar to window
        try:
            self.config(menu=menubar)
        except AttributeError:
            print('Error: Could not attach menu bar')

    def pdf_list(self, results):
        """
        Generate PDF start list or result list.

        Uses global configuration variables from checkboxes:
        - page_break: Insert page breaks between classes
        - one_active_class: Export only active class
        - for_start: Start list formatting
        - with_points: Include points column

        Args:
            results: True for result list, False for start list
        """
        pdf = pdfgen.Pdf()
        race = Race(self.db, race_number)

        if results:
            # Generate result list PDF
            pdf.result_list(
                race,
                one_active_class.get(),
                active_class,
                page_break.get(),
                with_points.get()
            )
        else:
            # Generate start list PDF
            pdf.start_list(
                race,
                for_start.get(),
                one_active_class.get(),
                active_class,
                page_break.get()
            )

    def xml_list(self):
        """
        Export results in IOF XML 3.0 format.

        Generates XML file compatible with national orienteering
        federation systems (Eventor).
        """
        xml = xmlgen.xml()
        xml.result_list(self.db, race_number)

    def find_99ers(self):
        """
        Run diagnostic check for control unit failures.

        A '99' code in punch data indicates a control unit malfunction.
        This method generates a report showing:
        - How many punches each control received
        - Which controls have 99 error codes
        - Summary of control health

        Output is printed to console.
        """
        race = Race(self.db, race_number)
        race.make_99_list()


class Tab(tk.Frame):
    """
    Individual tab in the notebook interface.

    Each tab represents a different display mode:
    - Administration: Split view with finished/out runners
    - Results: Three modes (klassevis/loop/siste)
    - Prewarn: Online control notifications
    - PoengO: Point orienteering scoring
    - Finish: Chronological finish list

    Auto-refresh:
    - Uses .after() callbacks to update displays
    - Boolean break flags control which displays are active
    - Prevents multiple simultaneous updates

    Layout:
    - Top frame: Controls (comboboxes, buttons, checkboxes)
    - Center: Three columns (left sidebar, main display, right sidebar)
    - Bottom: Logo banner
    """

    def __init__(self, name, *args, **kwargs):
        """
        Initialize tab with layout and controls.

        Args:
            name: Notebook parent widget
            **kwargs:
                width: Tab width in pixels
                height: Tab height in pixels
                tab_type: Type of tab ('adm'/'results'/'prewarn'/'poengo'/'finish')
                database: Database server identifier
                pre_database: Optional separate prewarn database
        """
        # Calculate layout dimensions
        width = int(kwargs['width'])
        height = int(kwargs['height'])
        left_w = int(width * 0.07)   # Sidebar width (7% of total)
        mid_w = int(width - 2 * left_w)  # Main display width
        self.table_w = mid_w

        # Instance variables
        self.runners = []
        self.buttons = []  # Class selection buttons (for admin tab)
        self.race_number = None
        self.class_name = None
        self.name = None
        self.print_results = False
        self.race = None

        # Break flags control which displays are updating
        # These prevent multiple simultaneous updates when switching tabs
        self.break_board_list = False  # Results klassevis mode
        self.break_loop_list = False   # Results loop mode
        self.break_last_list = False   # Results siste mode

        # Connect to database
        tab_type = kwargs['tab_type']
        self.db = Database(kwargs['database'])

        # Optional separate prewarn database
        if 'pre_database' in kwargs:
            self.pre_db = Database(kwargs['pre_database'])

        # Open log file (platform-specific path)
        if sys.platform == "win32":
            self.log_file = open("ospeaker.log", "w")
        else:
            self.log_file = open("/var/log/ospeaker.log", "w")

        # Initialize frame
        tk.Frame.__init__(self)

        # Create main layout containers
        self.top_frame = tk.Frame(self, bg='white')  # Top: Controls
        center = tk.Frame(self, bg='black')          # Center: Main display
        btm_frame = tk.Frame(self, bg='black')       # Bottom: Logo banner

        # Configure grid weights for responsive layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Position main containers
        self.top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=2, sticky="ew")

        # Create center three-column layout
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(0, weight=0)

        self.ctr_left = tk.Frame(center, bg='black', width=left_w, height=100)
        ctr_mid = tk.Frame(center, width=mid_w, height=100)
        ctr_right = tk.Frame(center, bg='black', width=left_w, height=100)

        self.ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_right.grid(row=0, column=2, sticky="nsew")

        # Logo banner (platform-specific path)
        pixels_x = 700
        pixels_y = int(pixels_x * 0.144)
        if sys.platform == "win32":
            # Use raw string to avoid escape sequence issues
            img = ImageTk.PhotoImage(
                Image.open(r"C:\Program Files (x86)\Brikkespy\images\black_MILO_banner.png")
                .resize((pixels_x, pixels_y))
            )
        else:
            img = ImageTk.PhotoImage(
                Image.open("/etc/black_MILO_banner.png")
                .resize((pixels_x, pixels_y))
            )

        label = tk.Label(btm_frame, bg="black", image=img)
        label.image = img  # Keep reference to prevent garbage collection
        label.pack(side="bottom", fill="both", expand="yes")

        # Get default heading configuration for result lists
        head = hdn.get_heading('resultater')
        heading = list(head.keys())
        columnwidth = [item[0] for item in head.values()]
        anchor = [item[1] for item in head.values()]

        # ===== TAB-SPECIFIC CONTENT =====

        if tab_type == 'adm':
            # Administration tab: Split view with finished/out runners

            # Top table: Finished runners
            self.finish = Table(
                ctr_mid,
                width=mid_w,
                height=height,
                row_height=30,
                heading=heading,
                columnwidth=columnwidth,
                anchor=anchor
            )

            # Bottom table: Runners still out
            self.out = Table(
                ctr_mid,
                width=mid_w,
                height=height,
                row_height=30,
                heading=heading,
                columnwidth=columnwidth,
                anchor=anchor
            )

            # Race selection combobox
            tk.Label(self.top_frame, text="Løp:").grid(row=0, column=1, sticky='w')

            # Safely handle empty race list
            races_names = []
            if self.db.races:
                try:
                    # Extract race names from database tuples
                    races_names = list(zip(*self.db.races))[1]
                except Exception:
                    # Fallback if race format is unexpected
                    races_names = [str(r) for r in self.db.races]

            self.combo_races = TTK.Combobox(
                self.top_frame,
                width=30,
                values=races_names,
                state='readonly'
            )
            self.combo_races.grid(row=0, column=2, sticky='w')
            self.combo_races.bind("<<ComboboxSelected>>", self.set_class_buttons)

            # Auto-select last race and build class buttons
            if races_names:
                last_index = len(races_names) - 1
                self.combo_races.current(last_index)
                global race_number
                race_number = last_index
                self.set_class_buttons()  # Build class buttons programmatically

            # PDF export checkboxes (use global variables for menu access)
            tk.Checkbutton(
                self.top_frame,
                text="Print med sideskift",
                variable=page_break
            ).grid(row=0, column=3, sticky='w')

            tk.Checkbutton(
                self.top_frame,
                text="Print aktiv_klasse",
                variable=one_active_class
            ).grid(row=0, column=4, sticky='w')

            tk.Checkbutton(
                self.top_frame,
                text="Print lister for start",
                variable=for_start
            ).grid(row=0, column=5, sticky='w')

            tk.Checkbutton(
                self.top_frame,
                text="Print lister med poeng",
                variable=with_points
            ).grid(row=0, column=6, sticky='w')

        elif tab_type == 'results':
            # Results tab: Three display modes

            self.board = Table(
                ctr_mid,
                width=mid_w,
                height=height,
                row_height=30,
                heading=heading,
                columnwidth=columnwidth,
                anchor=anchor
            )

            # Mode selection buttons
            class_button = tk.Button(
                self.top_frame,
                text='Klassevis',
                bg='white',
                command=partial(self.write_to_board)
            )
            loop_button = tk.Button(
                self.top_frame,
                text='Loop',
                bg='white',
                command=partial(self.write_to_loop)
            )
            last_button = tk.Button(
                self.top_frame,
                text='Siste',
                bg='white',
                command=partial(self.write_to_last)
            )

            class_button.grid(row=0, column=0)
            loop_button.grid(row=0, column=1)
            last_button.grid(row=0, column=2)

        elif tab_type == 'finish':
            # Finish list tab: Chronological finish list

            self.finish = Table(
                ctr_mid,
                width=mid_w,
                height=height,
                row_height=30,
                heading=heading,
                columnwidth=columnwidth,
                anchor=anchor
            )

            # Start display button
            class_button = tk.Button(
                self.top_frame,
                text='Klassevis',
                bg='white',
                command=partial(self.write_to_finish)
            )
            class_button.grid(row=0, column=0)

        elif tab_type == 'prewarn':
            # Prewarn tab: Online control notifications

            self.pre = Table(
                ctr_mid,
                width=mid_w,
                height=height,
                row_height=30,
                heading=heading,
                columnwidth=columnwidth,
                anchor=anchor
            )

            # Start prewarn display button
            self.button = tk.Button(
                self.top_frame,
                text='Forvarsel',
                command=partial(self.write_to_prewarn)
            )
            self.button.grid(row=0, column=0)

        elif tab_type == 'poengo':
            # PoengO tab: Point orienteering scoring

            # Use PoengO-specific heading configuration
            head = hdn.get_heading('poengo')
            heading = list(head.keys())
            columnwidth = [item[0] for item in head.values()]
            anchor = [item[1] for item in head.values()]

            self.poengo = Table(
                ctr_mid,
                width=mid_w,
                height=height,
                row_height=30,
                heading=heading,
                columnwidth=columnwidth,
                anchor=anchor
            )

            # PoengO display button
            self.button = tk.Button(
                self.top_frame,
                text='PoengO',
                command=partial(self.write_poengo)
            )
            self.button.grid(row=0, column=0)

            # CSV export button
            self.button = tk.Button(
                self.top_frame,
                text='csv',
                command=partial(self.write_poengo_csv)
            )
            self.button.grid(row=0, column=1)

            # Plot bonus points graph button
            self.plot_button = tk.Button(
                self.top_frame,
                text="Plot Bonuspoeng",
                bg="white",
                command=partial(self.plot_poengo_graph)
            )
            self.plot_button.grid(row=0, column=2)

    def __del__(self):
        """
        Cleanup method to close log file.

        Called automatically when Tab object is destroyed.
        """
        if hasattr(self, 'log_file') and self.log_file:
            self.log_file.close()

    # ===== DISPLAY CONTROL METHODS =====
    # These methods handle switching between different display modes
    # and setting break flags to stop previous updates

    def write_to_admin(self, class_name):
        """
        Switch to administration view for a specific class.

        Displays split view:
        - Top: Finished runners in class
        - Bottom: Runners still out in class

        Args:
            class_name: Class to display
        """
        global break_res, break_pre, break_adm
        break_res = True  # Stop result displays
        break_pre = True  # Stop prewarn display
        break_adm = False  # Start admin display
        self.write_admin_list(class_name)

    def write_to_board(self):
        """
        Switch to klassevis (class-by-class) result display.

        Cycles through each class, showing results for 5 seconds each.
        """
        global break_res, break_adm, break_pre
        break_res = False  # Start result display
        break_adm = True   # Stop admin display
        break_pre = True   # Stop prewarn display

        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number)
        self.class_names = iter(self.race.class_names)

        # Set internal break flags
        self.break_board_list = False  # Enable klassevis mode
        self.break_loop_list = True    # Disable loop mode
        self.break_last_list = True    # Disable siste mode

        self.write_board_list()

    def write_to_loop(self):
        """
        Switch to loop (continuous scroll) result display.

        Scrolls through all results continuously with one-line shifts.
        """
        global break_res, break_adm, break_pre
        break_res = False
        break_adm = True
        break_pre = True

        # Set internal break flags
        self.break_board_list = True   # Disable klassevis mode
        self.break_loop_list = False   # Enable loop mode
        self.break_last_list = True    # Disable siste mode

        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number)
        self.write_loop_list(0)

    def write_to_last(self):
        """
        Switch to siste (most recent finishers) display.

        Shows runners sorted by finish time (most recent first).
        """
        global break_res, break_adm, break_pre
        break_res = False
        break_adm = True
        break_pre = True

        # Set internal break flags
        self.break_board_list = True   # Disable klassevis mode
        self.break_loop_list = True    # Disable loop mode
        self.break_last_list = False   # Enable siste mode

        self.board.tree.delete(*self.board.tree.get_children())
        self.race = Race(self.db, race_number)
        self.write_last_list()

    def write_to_prewarn(self):
        """
        Switch to prewarn (online control) display.

        Shows runners who have punched at online controls.
        """
        global break_res, break_adm, break_pre
        break_res = True   # Stop result display
        break_adm = True   # Stop admin display
        break_pre = False  # Start prewarn display

        self.race = Race(self.db, race_number)
        self.write_prewarn_list()

    def write_to_finish(self):
        """
        Switch to finish list display.

        Shows chronological finish list across all classes.
        """
        self.race = Race(self.db, race_number)
        self.write_finish_list()

    # ===== AUTO-REFRESH DISPLAY METHODS =====
    # These methods update displays and schedule next refresh

    def write_admin_list(self, class_name):
        """
        Update administration split view for a class.

        Auto-refreshes every 5 seconds.

        Args:
            class_name: Class to display
        """
        global break_adm
        if not break_adm:
            global active_class
            active_class = class_name

            # Cancel previous scheduled updates if class changed
            if self.class_name:
                self.finish.after_cancel(self.finish_tree_alarm)
                self.out.after_cancel(self.out_tree_alarm)

            # Update top table: Finished runners
            self.finish.tree.delete(*self.finish.tree.get_children())
            result_list = self.race.make_result_list(class_name)
            self.write_table(result_list, 'res')
            # Schedule next update in 5 seconds
            self.finish_tree_alarm = self.finish.after(5000, self.write_admin_list, class_name)

            self.class_name = class_name

            # Update bottom table: Runners still out
            self.out.tree.delete(*self.out.tree.get_children())
            out_list = self.race.make_result_list(class_name, 'out')
            self.write_table(out_list, 'out')
            # Schedule next update in 5 seconds
            self.out_tree_alarm = self.out.after(5000, self.write_admin_list, class_name)

    def write_finish_list(self):
        """
        Update finish list display.

        Shows all finishers across all classes sorted by finish time.
        Auto-refreshes every 500ms.
        """
        self.finish.tree.delete(*self.finish.tree.get_children())

        # Collect all results from all classes
        all_lists = []
        for class_name in self.race.class_names:
            result_list = self.race.make_result_list(class_name)
            if result_list:
                all_lists.extend(result_list)

        # Filter out organizers and DNS
        finish_list = [i for i in all_lists if not ((i['tag'] == 'arr') or i['tag'] == 'dns')]
        # Sort by finish arrival time
        finish_list = sorted(finish_list, key=lambda i: str(i['Innkomst']))

        # Display results
        if finish_list:
            for name in finish_list:
                self.finish.LoadinTable(name)

        # Schedule next update in 500ms
        self.finish_tree_alarm = self.finish.after(500, self.write_finish_list)

    def write_board_list(self):
        """
        Update klassevis (class-by-class) display.

        Cycles through classes, showing each for 5 seconds.
        Auto-refreshes every 5 seconds.
        """
        global break_res
        if not self.break_board_list and not break_res:
            # Get next class
            class_name = self.get_next_element(self.class_names)

            # Restart iteration if we've reached the end
            if class_name is None:
                self.class_names = iter(self.race.class_names)
                class_name = self.get_next_element(self.class_names)

            # Update display
            self.board.tree.delete(*self.board.tree.get_children())
            result_list = self.race.make_result_list(class_name)

            # Only display if class has runners
            if result_list:
                class_list = []
                class_list.extend([hdn.line_shift()])        # Blank line
                class_list.extend([hdn.class_heading(class_name)])  # Class header
                class_list.extend(result_list)               # Results

                # Insert in reverse order (treeview inserts at top)
                for name in reversed(class_list):
                    self.board.LoadinTable(name)
            else:
                # Skip empty classes
                self.write_board_list()
                return

            # Schedule next update in 5 seconds
            self.board_tree_alarm = self.board.after(5000, self.write_board_list)

    def write_loop_list(self, loop):
        """
        Update loop (continuous scroll) display.

        Scrolls through all results one line at a time.
        Auto-refreshes every 1 second.

        Args:
            loop: Current scroll offset
        """
        global break_res
        if not self.break_loop_list and not break_res:
            # Generate complete result list
            loop_list = self.make_loop_list()

            # Rotate list by loop offset
            loop_list = loop_list[loop:] + loop_list[:loop]
            loop_length = len(loop_list)

            # Reset offset if we've scrolled past the end
            if loop >= loop_length:
                loop = 0

            # Update display
            self.board.tree.delete(*self.board.tree.get_children())
            for name in reversed(loop_list):
                self.board.LoadinTable(name)

            # Increment scroll offset
            loop += 1

            # Schedule next update in 1 second
            self.board_tree_alarm = self.board.after(1000, self.write_loop_list, loop)

    def write_last_list(self):
        """
        Update siste (most recent finishers) display.

        Shows runners sorted by finish time (most recent first).
        Auto-refreshes every 5 seconds.
        """
        global break_res
        if not self.break_last_list and not break_res:
            last_list = self.make_last_list()

            # Update display
            self.board.tree.delete(*self.board.tree.get_children())
            if last_list:
                for name in reversed(last_list):
                    self.board.LoadinTable(name)
            else:
                # Fall back to board list if no finishers yet
                self.write_board_list()
                return

            # Schedule next update in 5 seconds
            self.board_tree_alarm = self.board.after(5000, self.write_last_list)

    def write_prewarn_list(self):
        """
        Update prewarn (online control) display.

        Shows runners who have punched at online controls.
        Auto-refreshes every 5 seconds.
        """
        global break_pre
        if not break_pre:
            # Update display
            self.pre.tree.delete(*self.pre.tree.get_children())
            prewarn_list = self.race.make_prewarn_list()

            for name in reversed(prewarn_list):
                self.pre.LoadinTable(name)

            # Schedule next update in 5 seconds
            self.pre_tree_alarm = self.pre.after(5000, self.write_prewarn_list)

    def write_poengo(self):
        """
        Initialize PoengO display.

        Calculates and displays PoengO scores.
        """
        self.poengo.tree.delete(*self.poengo.tree.get_children())
        self.poeng = Race(self.db, race_number)
        self.write_poengo_list()

    def write_poengo_list(self):
        """
        Update PoengO results display.

        Shows point orienteering scores with bonus tracks.
        Auto-refreshes every 5 seconds.
        """
        self.poengo.tree.delete(*self.poengo.tree.get_children())

        # Calculate PoengO scores and filter for treeview display
        results_list = self.make_treeview_list(self.poeng.make_point_list())

        for name in reversed(results_list):
            self.poengo.LoadinTable(name)

        # Schedule next update in 5 seconds
        self.poengo_tree_alarm = self.poengo.after(5000, self.write_poengo_list)

    def write_poengo_csv(self):
        """
        Export PoengO results to CSV file.

        Writes to resultater.csv in current directory.
        Includes all control codes and bonus track columns.
        """
        poeng = Race(self.db, race_number)
        results = poeng.make_point_list()
        self.write_csv_list(results, poeng.heading)

    def write_csv_list(self, results, heading):
        """
        Write results to CSV file.

        Args:
            results: List of result dictionaries
            heading: List of column names

        Note:
            Removes internal columns 'klatresek' and 'sprintsek'
            which are used for sorting but not displayed.
        """
        result_writer = csv.writer(open("resultater.csv", "w"))

        # Remove internal sorting columns
        if 'klatresek' in heading:
            heading.remove('klatresek')
        if 'sprintsek' in heading:
            heading.remove('sprintsek')

        csv_list = []
        csv_list.append(heading)  # Header row

        # Convert result dictionaries to rows
        for result in results:
            res = []
            for key in heading:
                if key in result.keys():
                    res.append(result[key])
                else:
                    res.append('')  # Empty cell for missing data
            csv_list.append(res)

        result_writer.writerows(csv_list)

    def make_treeview_list(self, results):
        """
        Filter PoengO results for treeview display.

        Removes internal columns that shouldn't be displayed
        (individual control codes, lap times, etc.).

        Args:
            results: List of full PoengO result dictionaries

        Returns:
            List of filtered result dictionaries
        """
        tree_results = []
        for result in results:
            tree_results.append(self.poeng.set_poengo_text(result))
        return tree_results

    def write_table(self, data, table):
        """
        Write data to administration split view table.

        Args:
            data: List of runner dictionaries
            table: 'res' for finished table, 'out' for runners-out table
        """
        for name in reversed(data):
            if table == 'res':
                self.finish.LoadinTable(name)
            else:
                self.out.LoadinTable(name)

    def make_loop_list(self):
        """
        Generate complete result list for loop display.

        Combines results from all classes with headers and separators.

        Returns:
            List of result dictionaries and header dictionaries
        """
        loop_list = []
        for class_name in self.race.class_names:
            result_list = self.race.make_result_list(class_name)
            if result_list:  # Only include classes with runners
                loop_list.extend([hdn.line_shift()])             # Blank line
                loop_list.extend([hdn.class_heading(class_name)])  # Class header
                loop_list.extend(result_list)                    # Results
        return loop_list

    def make_last_list(self):
        """
        Generate list of most recent finishers.

        Returns:
            List of runner dictionaries sorted by finish time
        """
        return self.race.make_last_list()

    def get_next_element(self, my_itr):
        """
        Safely get next element from iterator.

        Args:
            my_itr: Iterator to get element from

        Returns:
            Next element, or None if iterator exhausted
        """
        try:
            return next(my_itr)
        except StopIteration:
            return None

    def set_class_buttons(self, event=None):
        """
        Create class selection buttons in administration tab.

        Builds a grid of buttons (one per class) in the left sidebar.
        Clicking a button displays that class in the split view.

        Args:
            event: Tkinter event (from combobox selection)
        """
        global race_number
        race_number = self.combo_races.current()
        self.race = Race(self.db, race_number)

        # Remove old buttons safely
        if self.buttons:
            for button in self.buttons:
                try:
                    button.destroy()
                except Exception:
                    pass
            self.buttons.clear()

        # Calculate grid layout
        # If more than 30 classes, split into two columns
        i = 0
        s = 0  # Row counter
        j = 0  # Column counter

        if len(self.race.class_names) > 30:
            nrow = int(len(self.race.class_names) / 2) + 1
        else:
            nrow = len(self.race.class_names)

        # Create button for each class
        for class_name in self.race.class_names:
            if class_name:
                btn = tk.Button(
                    self.ctr_left,
                    text=class_name,
                    command=partial(self.write_to_admin, class_name)
                )
                self.buttons.append(btn)
                self.buttons[-1].grid(row=s, column=j, padx=5)

                i += 1
                s += 1

                # Move to second column after nrow buttons
                if s >= nrow:
                    j += 1
                    s = 0

    def plot_poengo_graph(self):
        """
        Display bonus points bar chart for PoengO classes.

        Creates matplotlib chart showing bonus points by age class:
        - D classes (blue bars)
        - H classes (orange bars)
        - Other classes (green bars)

        Chart is grouped by age category with D/H side-by-side.
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # Get bonus points configuration from race
        race = Race(self.db, race_number)
        data = race.get_bonus_points()

        # Split data by class prefix
        d_data = {k[2:]: v for k, v in data.items() if k.startswith("D")}
        h_data = {k[2:]: v for k, v in data.items() if k.startswith("H")}
        other_data = {k: v for k, v in data.items() if not k.startswith("D") and not k.startswith("H")}

        # Get all unique age groups from D and H classes
        groups = sorted(set(d_data.keys()) | set(h_data.keys()))

        # Get values for each group (0 if class doesn't exist)
        d_values = [d_data.get(g, 0) for g in groups]
        h_values = [h_data.get(g, 0) for g in groups]

        # Other classes as separate groups
        other_groups = list(other_data.keys())
        other_values = list(other_data.values())

        # Set up x-axis positions
        x_main = np.arange(len(groups))  # D/H positions
        x_other = np.arange(len(other_groups)) + len(groups) + 1  # Other after gap

        width = 0.28  # Bar width

        plt.figure(figsize=(14, 6))

        # D bars (blue)
        plt.bar(x_main - width, d_values, width, label="D", color="tab:blue")

        # H bars (orange)
        plt.bar(x_main, h_values, width, label="H", color="tab:orange")

        # Other bars (green)
        plt.bar(x_other, other_values, width, label="Andre klasser", color="tab:green")

        # X-axis labels: D/H groups + gap + other groups
        xticks = list(groups) + [""] + other_groups
        x_positions = list(x_main) + [len(groups)] + list(x_other)

        plt.xticks(x_positions, xticks, rotation=45)

        plt.ylabel("Poeng")
        plt.title("Bonuspoeng – D, H og øvrige klasser")
        plt.legend()
        plt.tight_layout()
        plt.show()


class Table(TTK.Frame):
    """
    Reusable treeview table component for displaying runner data.

    Features:
    - Configurable columns, widths, and alignment
    - Row height and font size control
    - Tag-based color coding (finished/out/DSQ/DNS/recent)
    - Scrollbar support
    - Auto-sizing based on screen dimensions

    Tag colors:
    - 'title': Green (class headings)
    - 'ute': Orange (runners still out)
    - 'inne': White (finished)
    - 'last': Green (recent finishers)
    - 'dsq': Red (disqualified)
    - 'dns': Grey (did not start)
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize table component.

        Args:
            parent: Parent widget
            **kwargs:
                width: Table width in pixels
                height: Table height in pixels
                row_height: Height of each row in pixels
                heading: List of column names
                columnwidth: List of column width ratios (0.0-1.0)
                anchor: List of column alignments ('w'/'center'/'e')
        """
        TTK.Frame.__init__(self, parent)

        # Store configuration
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.rowheight = kwargs['row_height']
        self.heading = kwargs['heading']
        self.anchor = kwargs['anchor']
        self.columnwidth = kwargs['columnwidth']

        # Calculate number of visible rows
        self.rows = int(self.height / self.rowheight)

        # Create treeview
        self.tree = self.CreateUI()

        # Configure tag colors
        self.tree.tag_configure('title', background='green')
        self.tree.tag_configure('ute', background='orange')
        self.tree.tag_configure('inne', background="white")
        self.tree.tag_configure('last', background="green")
        self.tree.tag_configure('dsq', background='red')
        self.tree.tag_configure('dns', background='grey')
        self.tree.tag_configure('old', background='white')

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky='n')

    def CreateUI(self):
        """
        Create treeview widget with columns and scrollbar.

        Returns:
            Configured treeview widget
        """
        # Set row height and font
        style = TTK.Style()
        style.configure('Treeview', rowheight=self.rowheight, font="Helvetica 16 bold")

        # Create treeview
        tv = TTK.Treeview(self, height=self.rows, style='Treeview')

        # Add scrollbar
        vsb = TTK.Scrollbar(self, orient="vertical", command=tv.yview)
        vsb.place(x=-17 + self.width, y=20, height=int(self.rowheight * self.rows))
        tv.configure(yscrollcommand=vsb.set)

        # Configure columns
        tv['columns'] = tuple(self.heading)

        # First column (startnummer) in tree column
        tv.heading("#0", text='Startnum', anchor='center')
        tv.column("#0", anchor="center", width=int(self.width * 0.07))

        # Additional columns
        i = 0
        for title in self.heading:
            tv.heading(title, text=title)
            tv.column(title, anchor=self.anchor[i], width=int(self.width * self.columnwidth[i]))
            i += 1

        tv.grid(sticky='n')
        return tv

    def LoadinTable(self, entry):
        """
        Insert a row into the table.

        Inserts at top (index 0) so most recent data appears first.

        Args:
            entry: Dictionary with runner data
                Must include 'Startnr', 'tag', and all heading columns
        """
        # Ensure start number is set
        if not entry['Startnr']:
            entry['Startnr'] = ' '

        # Build value tuple from heading columns
        a = []
        for title in self.heading:
            a.append(entry[title])
        a = tuple(a)

        # Insert row at top with color tag
        self.tree.insert('', 0, text=entry['Startnr'], values=(a), tags=entry['tag'])
