#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
brikkesys.py - Database abstraction layer for Brikkesys MySQL database

This module provides a Database class that handles all interactions with the
Brikkesys orienteering race management database. It reads race information,
runner data, class definitions, online control punches, and eventor integration data.

Key Features:
- Automatic handling of case-sensitive vs case-insensitive database tables
- Parameterized queries to prevent SQL injection
- Connection pooling and transaction management
- Logging of database errors
- Support for multiple database servers (local, remote race PCs)

Database Connection:
- Connection parameters configured in config_database.py
- Supports both Windows and Linux platforms with different log paths
"""

import config_database as config
import pymysql
import sys
from datetime import datetime


class Database:
    """
    Database abstraction layer for Brikkesys MySQL database.

    Handles connections to Brikkesys race management database and provides
    methods to read races, runners, classes, online controls, and eventor data.

    The Brikkesys database schema varies in case sensitivity between installations.
    This class automatically tries uppercase table names first, then falls back
    to lowercase if the query fails.

    Attributes:
        db: PyMySQL database connection object
        races: List of race tuples from RACES table
        race_ids: List of race IDs (currently unused)
        cursor: Database cursor for executing queries
        log_file: File handle for error logging
    """

    def __init__(self, ip_address):
        """
        Initialize database connection and read available races.

        Args:
            ip_address: Database server identifier (e.g., 'local', 'Milo', 'Klara')
                       or actual IP address. Maps to connection config in config_database.py

        Creates database connection, opens log file, and loads race list.
        Log file location depends on platform:
        - Windows: ospeaker.log in current directory
        - Linux: /var/log/ospeaker.log
        """
        # Establish database connection using config from config_database.py
        self.db = pymysql.connect(**config.get_config(ip_address))
        self.races = []
        self.race_ids = []
        self.cursor = self.db.cursor()

        # Open log file (platform-specific path)
        if sys.platform == "win32":
            self.log_file = open("ospeaker.log", "w")
        else:
            self.log_file = open("/var/log/ospeaker.log", "w")

        # Load available races from database
        try:
            self.read_races()
        except Exception as e:
            self.log_file.write("No races in database {0}: {1}\n".format(str(ip_address), str(e)))
            self.log_file.flush()

    def __del__(self):
        """
        Cleanup method to ensure log file is closed properly.

        Called automatically when Database object is destroyed.
        Prevents resource leaks by closing the log file handle.
        """
        if hasattr(self, 'log_file') and self.log_file:
            self.log_file.close()

    def read_version(self):
        """
        Read MySQL server version.

        Diagnostic method to check database connectivity and version.
        Currently does not return the version, just executes the query.

        Returns:
            None (could be modified to return version string)
        """
        self.cursor.execute("SELECT VERSION()")
        data = self.cursor.fetchone()
        # Could return data here if needed for diagnostics

    def read_online(self, race_id):
        """
        Read online control punch data for prewarn system.

        Online controls are checkpoints along the course that transmit when
        runners punch them. This data is used for the prewarn system to show
        runners approaching certain points.

        Args:
            race_id: Race ID to fetch online control data for

        Returns:
            List of tuples containing online control punch records
            Each tuple contains: (id, race_id, ecard_no, control_code, punch_time, ...)

        Note:
            Tries uppercase table name ONLINECONTROLS first, then lowercase.
            This handles database case sensitivity variations.
        """
        # Commit any pending transactions to ensure we read latest data
        self.db.commit()

        # Try uppercase table name first (newer Brikkesys installations)
        sql = "SELECT * FROM ONLINECONTROLS WHERE RACEID = %(race_id)s"
        try:
            # Use parameterized query to prevent SQL injection
            self.cursor.execute(sql, {'race_id': race_id})
            return self.cursor.fetchall()
        except Exception:
            # Fallback: Try lowercase table name (older Brikkesys installations)
            try:
                sql = "SELECT * FROM onlinecontrols WHERE raceid = %(race_id)s"
                self.cursor.execute(sql, {'race_id': race_id})
                return self.cursor.fetchall()
            except Exception as e:
                # Log error if both attempts fail
                self.log_file.write("Unable to fetch online controls {0}: {1}\n".format(str(sql), str(e)))
                self.log_file.flush()
                return []

    def read_eventor_personid(self, person_id):
        """
        Read Eventor person ID mapping for a runner.

        Eventor is the national orienteering federation's registration system.
        This table maps local Brikkesys person IDs to national Eventor IDs
        for result export and integration.

        Args:
            person_id: Local Brikkesys person ID

        Returns:
            List of tuples with Eventor person data, or empty list on error
        """
        sql = "SELECT * FROM eventor_personid WHERE bid = %(person_id)s"
        try:
            self.cursor.execute(sql, {'person_id': person_id})
            return self.cursor.fetchall()
        except Exception as e:
            self.log_file.write("Unable to fetch eventor person {0}: {1}\n".format(str(sql), str(e)))
            self.log_file.flush()
            return []

    def read_eventor_club(self, club_id):
        """
        Read Eventor club information.

        Maps local club IDs to Eventor organization IDs for result export.

        Args:
            club_id: Eventor organization ID

        Returns:
            List of tuples with club data (name, short name, etc.), or empty list on error
        """
        sql = "SELECT * FROM eventor_clubs WHERE organisationid = %(club_id)s"
        try:
            self.cursor.execute(sql, {'club_id': club_id})
            return self.cursor.fetchall()
        except Exception as e:
            self.log_file.write("Unable to fetch eventor club {0}: {1}\n".format(str(sql), str(e)))
            self.log_file.flush()
            return []

    def read_invoicelevel(self, race_id):
        """
        Read invoice/fee levels for a race.

        Invoice levels define entry fees for different runner categories.
        Used for XML result export and financial reporting.

        Args:
            race_id: Race ID to fetch invoice levels for

        Returns:
            List of tuples with invoice level data, or empty list on error
        """
        sql = "SELECT * FROM invoicelevels WHERE raceid = %(id)s"
        try:
            self.cursor.execute(sql, {'id': race_id})
            return self.cursor.fetchall()
        except Exception as e:
            self.log_file.write("Unable to fetch invoice levels {0}: {1}\n".format(str(sql), str(e)))
            self.log_file.flush()
            return []

    def read_races(self):
        """
        Read all races from database.

        Populates self.races with all available races. This is called during
        initialization to build the race selection list in the GUI.

        Race tuple structure:
            [0] = Race ID (primary key)
            [1] = Race name
            [2] = Race date
            [3+] = Additional race metadata

        Note:
            Tries uppercase table name RACES first, then lowercase races.
            Results stored in self.races attribute.
        """
        # Try uppercase table name first
        sql = "SELECT * FROM RACES"
        try:
            self.cursor.execute(sql)
            self.races = self.cursor.fetchall()
        except Exception:
            # Fallback to lowercase table name
            try:
                sql = "SELECT * FROM races"
                self.cursor.execute(sql)
                self.races = self.cursor.fetchall()
            except Exception as e:
                # Log error if both attempts fail
                self.log_file.write("Unable to fetch races {0}: {1}\n".format(str(sql), str(e)))
                self.log_file.flush()
                self.races = []

    def read_names(self, race_id):
        """
        Read all runners (names) for a specific race.

        This is the core method that fetches runner data including registration
        details, start times, finish times, and control punch data.

        Args:
            race_id: Race ID to fetch runners for

        Returns:
            List of runner tuples. Each tuple contains:
                [0]  = Runner ID (primary key)
                [2]  = Runner name
                [3]  = Club name
                [4]  = Class ID
                [6]  = E-card number (brikkenummer)
                [7]  = Start number
                [8]  = Finish time (timedelta)
                [10] = Status code (I/A/D/N/X/E/H/C/P/V)
                [11] = Control codes with timestamps ("101 245, 103 312,")
                [12] = Finish arrival timestamp
                [14] = Start time (datetime)
                [16] = Course ID
                [17] = Control codes only (space-separated)
                [18] = Alternative start time field
                [24] = Invoice level

        Note:
            Commits pending transactions before reading to ensure fresh data.
            Tries uppercase NAMES table first, then lowercase names.
        """
        # Commit to ensure we read the latest data (important for real-time updates)
        self.db.commit()

        # Try uppercase table name first
        sql = "SELECT * FROM NAMES WHERE RACEID = %(race_id)s"
        try:
            self.cursor.execute(sql, {'race_id': race_id})
            return self.cursor.fetchall()
        except Exception:
            # Fallback to lowercase table name
            try:
                sql = "SELECT * FROM names WHERE raceid = %(race_id)s"
                self.cursor.execute(sql, {'race_id': race_id})
                return self.cursor.fetchall()
            except Exception as e:
                # Log error if both attempts fail
                self.log_file.write("Unable to fetch names {0}: {1}\n".format(str(sql), str(e)))
                self.log_file.flush()
                return []

    def read_names_from_class(self, race_id, class_id):
        """
        Read all runners for a specific race and class.

        Filtered version of read_names() that returns only runners in a
        specific class. More efficient when processing single classes.

        Args:
            race_id: Race ID to fetch runners from
            class_id: Class ID to filter by (e.g., H21, D18, etc.)

        Returns:
            List of runner tuples (same structure as read_names())
            Only includes runners in the specified class.

        Note:
            Commits pending transactions before reading.
            Tries uppercase NAMES/CLASSID first, then lowercase.
        """
        # Commit to ensure we read the latest data
        self.db.commit()

        # Try uppercase table and column names first
        sql = "SELECT * FROM NAMES WHERE RACEID = %(race_id)s AND CLASSID = %(class_id)s"
        try:
            self.cursor.execute(sql, {'race_id': race_id, 'class_id': class_id})
            return self.cursor.fetchall()
        except Exception:
            # Fallback to lowercase table and column names
            try:
                sql = "SELECT * FROM names WHERE raceid = %(race_id)s AND classid = %(class_id)s"
                self.cursor.execute(sql, {'race_id': race_id, 'class_id': class_id})
                return self.cursor.fetchall()
            except Exception as e:
                # Log error with both SQL and class_id for debugging
                self.log_file.write("Unable to fetch names {0} for class {1}: {2}\n".format(
                    str(sql), str(class_id), str(e)
                ))
                self.log_file.flush()
                return []

    def read_classes(self, race_id):
        """
        Read all classes and courses for a specific race.

        Classes define age/gender categories (e.g., H21, D18).
        Courses define the physical route on the map.
        Both are stored in the same table, distinguished by a type field.

        Args:
            race_id: Race ID to fetch classes/courses for

        Class/Course tuple structure:
            [0]  = Class/Course ID (primary key)
            [1]  = Name
            [4]  = Control codes (space-separated string)
            [6]  = Race ID
            [14] = Type (0 = Class, 1 = Course)

        Note:
            Results stored in self.classes attribute.
            Tries uppercase CLASSES table first, then lowercase.
        """
        # Try uppercase table name first
        sql = "SELECT * FROM CLASSES WHERE RACEID = %(race_id)s"
        try:
            self.cursor.execute(sql, {'race_id': race_id})
            self.classes = self.cursor.fetchall()
        except Exception:
            # Fallback to lowercase table name
            try:
                sql = "SELECT * FROM classes WHERE raceid = %(race_id)s"
                self.cursor.execute(sql, {'race_id': race_id})
                self.classes = self.cursor.fetchall()
            except Exception as e:
                # Log error with SQL and race_id for debugging
                self.log_file.write("Unable to fetch classes {0} for race {1}: {2}\n".format(
                    str(sql), str(race_id), str(e)
                ))
                self.log_file.flush()
                self.classes = []

    def read_start_numbers(self):
        """
        Read start numbers from separate prewarn database.

        This is used with the alternative prewarn system that uses a dedicated
        database instead of online controls. The prewarn database stores start
        numbers as runners pass checkpoints.

        Returns:
            List of tuples containing start number records, or empty list on error

        Note:
            This reads from a DIFFERENT database than the main Brikkesys database.
            The connection must be configured separately in config_database.py.
            Tries lowercase startnumbers first, then uppercase STARTNUMBERS.
        """
        # Commit to ensure we read the latest data
        self.db.commit()

        # Try lowercase table name first (different convention for this table)
        sql = "SELECT * FROM startnumbers"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception:
            # Fallback to uppercase table name
            try:
                sql = "SELECT * FROM STARTNUMBERS"
                self.cursor.execute(sql)
                return self.cursor.fetchall()
            except Exception as e:
                # Log error if both attempts fail
                self.log_file.write("Unable to fetch start numbers {0}: {1}\n".format(str(sql), str(e)))
                self.log_file.flush()
                return []
