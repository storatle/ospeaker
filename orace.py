#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
orace.py - Core race data model and business logic for BrikkeSpy/OSpeaker

This module contains the Race class which handles:
- Reading race data from Brikkesys database
- Processing result lists and start lists
- Calculating PoengO scores with bonus points and time penalties
- Managing prewarn (online control) data
- Diagnostic tools for checking control unit failures

Database Field Mappings (from NAMES table):
    name[0]  = Runner ID
    name[2]  = Runner name
    name[3]  = Club name
    name[4]  = Class ID
    name[6]  = E-card number (brikkenummer)
    name[7]  = Start number
    name[8]  = Finish time (timedelta)
    name[10] = Status tag (I/A/D/N/X/E/H/C/P/V)
    name[11] = Control codes with timestamps (e.g., "101 245, 103 312,")
    name[12] = Finish arrival timestamp
    name[14] = Start time (datetime)
    name[16] = Course ID
    name[17] = Control codes only (space-separated string)
    name[18] = Alternative start time field
    name[24] = Invoice level
"""

from datetime import datetime, timedelta
from collections import Counter
import time
import math
import config_database as config
import config_brikkespy as config_spy
import sys
import os
import importlib.util

# Dynamic PoengO configuration loading:
# Check current working directory first (allows event-specific overrides),
# then fall back to script directory
cwd_config_path = os.path.join(os.getcwd(), "config_poengo.py")
if os.path.exists(cwd_config_path):
    # Add current working directory to sys.path
    sys.path.insert(0, os.getcwd())
    import config_poengo as poengo
    print(f"Config loaded from current working directory: {cwd_config_path}")
else:
    # Step 2: Fallback to the directory where the script resides
    main_script_dir = os.path.dirname(__file__)
    main_config_path = os.path.join(main_script_dir, "config_poengo.py")
    if os.path.exists(main_config_path):
        # Add script's directory to sys.path
        sys.path.insert(0, main_script_dir)
        import config_poengo as poengo
        print(f"Config loaded from script's main directory: {main_config_path}")
    else:
        print("No config.py found in either the current working directory or the script's directory")

class Race:
    """
    Core race data model representing a single orienteering race.

    Handles all race-related operations including:
    - Result list generation
    - Start list generation
    - PoengO scoring calculations
    - Prewarn (online control) processing
    - Diagnostic tools for control failures
    """
    def __init__(self, db , num):
        self.runners = []
        self.classes = []
        self.courses = []
        self.class_names=[]
        self.db = db
        self.idx = 0
        self.get_race(num)
        self.get_classes()

        if sys.platform == "win32":
            self.log_file = open("ospeaker.log", "w")
        else:
            self.log_file = open("/var/log/ospeaker.log", "w")

    def get_race(self, race):
        """Load race metadata from database by index."""
        self.race = self.db.races[race]
        self.race_id = self.race[0]      # Race ID (primary key)
        self.race_name = self.race[1]    # Race name/title
        self.race_date = self.race[2]    # Race date

    def get_prewarn(self, race_id):
        """Load online control data for prewarn system."""
        self.prewarn = self.db.read_online(race_id)

    def get_names(self):
        """Fetch all runners (names) for this race from database."""
        self.runners=self.db.read_names(self.race_id)

    def get_classes(self):
        """
        Load all classes and courses for this race.

        Database row[14] determines type:
        - 0 = Class (age/gender category)
        - 1 = Course (physical route on map)
        """
        self.db.read_classes(self.race_id)
        for row in self.db.classes:
            if row[6] == self.race_id:
                if row[14] == 0:  # Class entry
                    self.class_names.append(row[1])
                    self.classes.append(row)
                elif row[14] == 1:  # Course entry
                    self.courses.append(row)
 
    def find_runner_2(self, startnum):
        """Find runner by start number (used with separate prewarn database)."""
        self.get_names()  # Refresh runner data from database
        for name in self.runners:
            if name[7] == int(startnum):
                return name

    def find_runner(self, ecardno):
        """Find runner by e-card number (brikkenummer)."""
        for name in self.runners:
            if name[6] == int(ecardno):
                return name

    def find_class_name(self, class_id):
        """Convert class ID to class name string."""
        for row in self.classes:
            if row[0] == class_id:
                return row[1]

    def find_class(self, class_name):
        """
        Fetch all runners in a specific class from database.

        Args:
            class_name: Name of class, or 'all' for all runners

        Returns:
            List of runner tuples from database
        """
        if class_name == 'all':
            return self.db.read_names(self.race_id)
        else:
            for id in self.classes:
                if id[1] == class_name:
                    class_id = id[0]
                    return self.db.read_names_from_class(self.race_id, class_id)

    def make_start_list(self, class_name):
        """
        Generate start list sorted by start time.

        Args:
            class_name: Class to generate list for

        Returns:
            List of runner dictionaries with start details
        """
        start_list = []
        data = self.find_class(class_name)
        if data:
            # Sort by start time (name[14])
            data = sorted(data, key=lambda tup: str(tup[14]))
            for name in data:
                name = list(name)
                text = self.set_runner_details(name)
                start_list.append(text)

        return start_list

    def make_last_list(self, *args):
        """
        Generate list of most recent finishers across all classes.

        Sorted by finish arrival time (most recent first).
        Excludes runners still out in forest ('ute').
        Recent finishers (within 1 minute) get 'last' tag for highlighting.

        Returns:
            List of runner dictionaries sorted by finish time
        """
        ute = []
        dns = []
        dsq = []
        arr = []
        names = []
        last_list = []
        self.get_names()
        names = self.runners  # All runners

        for name in names:
            text = self.set_runner_details(name)
            text['tag'] = self.set_tag(name[10])

            # For finished runners, check if they're recent (within 1 min)
            if text['tag'] == 'inne':
                if name[12]:  # name[12] = finish arrival timestamp
                    text['tag'] = self.check_inn_time(name[12])
                # Get placement and time difference from their class result
                result = (next(x for x in self.make_result_list(text['Klasse']) if x['Navn'] == text['Navn']))
                text['Plass'] = result['Plass']
                text['Differanse'] = result['Differanse']

            # Separate runners by status
            if text['tag'] == 'dns':
                text['Tid'] = str('DNS')
                dns.append(text)
                continue  # DNS runners shown at end
            if text['tag'] == 'ute':
                ute.append(text)
            if text['tag'] == 'dsq':
                text['Tid'] = str('DSQ')
                dsq.append(text)
            if text['tag'] == 'arr':
                arr.append(text)
            else:
                last_list.append(text)

        # Sort by finish arrival time (most recent first)
        last_list = (sorted(last_list, key=lambda i: str(i['Innkomst']), reverse=True))
        last_list.extend(dns)
        last_list.extend(arr)
        # Exclude runners still out in forest
        liste=[x for x in last_list if x not in ute]
        return liste
    
    def make_result_list(self, class_name, *args):
        """
        Generate result list for a specific class.

        Calculates placements, time differences from winner, and points.
        Handles special cases:
        - Unranked classes (no placement numbers)
        - No-time classes (show only "fullført"/completed)
        - Runners still out (calculate elapsed time)

        Args:
            class_name: Class to generate results for
            *args: Optional 'out' to return only runners still out

        Returns:
            List of runner dictionaries with results, sorted by time
        """
        urangert = False
        uten_tid = False
        results = []
        vinnertid = None
        result_list = []
        ute = []
        dns = []
        dsq = []
        arr = []
        plass = 0

        # Fetch all runners in class
        data = self.find_class(class_name)
        for name in data:
            name = list(name)
            # Convert database status code to display tag
            name[10] = self.set_tag(name[10])
            # For runners not yet finished, calculate elapsed time
            if not name[8] or name[10] =='ute':
                name[8] = self.get_time(name[14])  # name[14] = start time
            results.append(name)

        # Check for special class types from config
        if class_name in config_spy.unranked_classes():
            self.print_results = False
            urangert = True
        elif class_name in config_spy.no_time_classes():
            uten_tid = True
        else:
            # Standard ranked class - sort by finish time
            results = sorted(results, key=lambda tup: str(tup[8]))

        # Calculate time differences and points relative to winner
        for name in results:
            text = self.set_runner_details(name)

            if name[14]:  # Check if runner has start time
                text['Starttid'] = str(name[14].time())
            if uten_tid:
                text['Tid'] = str('fullført')

            # Separate runners by status
            if text['tag'] == 'ute':
                ute.append(text)
            if text['tag'] == 'dsq' and not uten_tid:
                text['Tid'] = str('DSQ')
                dsq.append(text)
                continue
            if text['tag'] == 'dns':
                text['Tid'] = str('DNS')
                dns.append(text)
                continue
            if text['tag'] == 'arr':
                text['Tid'] = str('Arrangør')
                arr.append(text)
                continue

            # Set winner time (first finisher in sorted list)
            if not vinnertid:
                vinnertid = name[8]

            if urangert or uten_tid:
                result_list.append(text)
            else:
                plass += 1
                text['Plass'] = str(plass)
                # Calculate time difference from winner
                try:
                    diff = name[8] - vinnertid
                    text['Differanse'] = str(diff)

                    # Calculate points: 100 points for winner, down to min 50 points
                    # Formula: 100 - 50 * (time_behind / winner_time)
                    text['Poeng'] = int(round(100 - 50 * (name[8]-vinnertid) / vinnertid))
                    if text['Poeng'] <= 50:
                        text['Poeng'] = str(50)
                    else:
                        text['Poeng'] = str(text['Poeng'])
                except:
                    diff = None
                result_list.append(text)

        # Remove runners still out from main list
        liste=[x for x in result_list if x not in ute]

        # Recalculate placements after removing 'ute' runners
        plass = 0
        for name in liste:
            plass += 1
            name['Plass'] = str(plass)

        # Add non-finishers at end
        liste.extend(dsq)
        liste.extend(dns)
        liste.extend(arr)

        # Optional: return only runners still out
        for arg in args:
            if arg == 'out':
                return ute
        return liste

    def make_prewarn_list(self):
        """
        Generate prewarn list from online control punches.

        Shows runners who have punched at online controls, useful for
        tracking runner progress through the course.

        prewarn[2] = e-card number to match against runner

        Returns:
            List of runners who have punched online controls
        """
        prewarn_list = []
        self.get_prewarn(self.race_id)
        self.get_names()  # Refresh runner data from database
        print("make_prewarn self.prewarn: {}".format(self.prewarn))

        for prewarn in self.prewarn:
            runner = self.find_runner(prewarn[2])  # Match by e-card number
            if runner is not None:
                runner = list(runner)
                runner[10] = self.set_tag(runner[10])

                # For runners still out, calculate elapsed time
                if runner[10] == 'ute':
                    try:
                        runner[8] = self.get_time(runner[14])
                    except:
                        if runner[10] == 'dns':
                            runner[8] = 'DNS'
                if not runner[8]:
                    runner[8] = runner[10]

                # Avoid duplicates by e-card number
                if not any(str(runner[6]) in d['Brikkenr'] for d in prewarn_list):
                      prewarn_list.insert(0, self.set_runner_details(runner))

        return prewarn_list

    def find_indices(list_to_check, item_to_find):
        """Helper function to find all indices of an item in a list."""
        indices = []
        for idx, value in enumerate(list_to_check):
            if value == item_to_find:
                indices.append(idx)
        return indices

    def check_disk_reason(self):
        """
        Diagnostic tool to analyze disqualifications.

        For each disqualified runner, compares their punched controls
        against the required course controls to identify which controls
        were missed or punched incorrectly.

        Prints summary of missing controls across all DSQ runners.
        """
        self.get_names();
        names = self.runners # alle løpere
        race = self.race
        faults = []
        drop_name = []
        #print(race)
        print('-------------------------------------------------')
        x = race[2]
        print(x.strftime("%d-%m-%y") + ' '+ race[1])
        print("Sjekker antall disk og hvilke brikker som gir disk")
        print()
        for name in names: # for hver løper
            startTid = name[18]
            items = self.set_runner_details(name)
            if(items['tag'] == 'D'):


                    #print(name)
                    course_id = items['Courseid']
                    if not course_id:
                        print(items['Navn'])
                        course_id = config_spy.course_id(items['Navn'])

                    #print(course_id)
                    ind = [idx for idx, value in enumerate(self.courses) if value[0] == course_id]
                    if ind:
                        course_name = self.courses[ind[0]][1]
                    else:
                
                        course_name = ''
                    
                    
                    print('Navn: {}, Løype {}'.format(items['Navn'], course_name))
                    #print()
                    print('Brikkekoder: {}'.format(items['Poster']))
                    if ind:
                        course_codes = (self.courses[ind[0]][4]).split()
                        print('Løypekoder: {} '.format(self.courses[ind[0]][4]))

                        codes = items['Poster'].split()
                        equals = (set(course_codes) & set(codes))
                        #print('Equals: {}'.format(' '.join(equals)))
                        #print(set(course_codes).difference(codes))
                        diff = Counter(course_codes)-Counter(codes)
                        if config_spy.drop_diskcheck(items['Navn']):
                                drop_name.append(items['Navn'])
                        for key, value in diff.items():
                            print('{} avik på kode {}'.format(value, key))
                            if not config_spy.drop_diskcheck(items['Navn']):
                                faults.append(key)
                        #print('------')
                        #print('{}'.format(diff))
                        #print(set(course_codes).difference(equals)) 
                        #print('Equals: {}'.format(' '.join(equals)))
                        #print(set(course_codes).difference(codes))
                        print('---------------------------------------------------------------')
        print()
        num_faults = Counter(sorted(faults))
        for key, value in num_faults.items():
            print('{} avik på kode {}'.format(value, key))
        print()
        print('Disse ble droppet i oppsummeringen over:')
        for name in drop_name:
            print (name)

        print()

                   
    def make_99_list(self):
        """
        Diagnostic tool for checking control unit failures.

        A '99' code in the punch data indicates a control unit malfunction.
        This method:
        1. Counts punches per control across all runners
        2. Identifies which controls have '99' error codes
        3. Prints summary report of control health

        Accessible via File → Status menu.
        """
        codes= None
        all_codes = {}
        fail = []
        course_codes = []
        self.get_names();
        names = self.runners # alle løpere
        race = self.race    
        courses = self.courses
        for course in courses:
            #print(course[0])
            course_codes = list(set(course_codes + course[4].split()))
            #print(course_codes)

        print(race)
        print('-------------------------------------------------')
        x = race[2]
        print(x.strftime("%d-%m-%y") + ' '+race[1])
        print("Antall stemplinger per post og antall enheter med 99-kode")
        for name in names: # for hver løper
            startTid = name[18]
            #print(name)
            items = self.set_runner_details(name)
            #print(items)
            codes = items['Poster']
            #print(items['Starttid'])
            times = items['Times']
            if (codes != None):
                #print(codes)
                codes = sorted(codes.split())
                ind = [idx for idx, value in enumerate(codes) if value == '99']       
                times = times.split()
                #print(times)
                times = [y.replace(',', '') for y in times]
                for code in codes:
                    if code in course_codes:
                        
            #        print(code)
                        if (code not in all_codes):
                            all_codes[code] = {}
                            all_codes[code]['num'] = 0 
                            all_codes[code]['times'] = {}
                            all_codes[code]['99'] = False
                        all_codes[code]['num'] += 1
                        ind = times.index(code)
                    #print(code)
                        num = (all_codes[code]['num'])
                        all_codes[code]['times'][num] = startTid + timedelta(0, int(times[ind+1]))
            if (times != None):
                #print(times)
                if ('99' in times ):
                     ind = times.index('99')-2 # Hva om det er flere?
                     #print('ind med 99er: {}'.format(ind))
                     if times[ind] in course_codes:
                         if (ind > 0 and times[ind] not in fail):
                             print("Sjekker om det er 99 i times, {}".format(times[ind]))
                             all_codes[times[ind]]['99'] = True
                             #print('kode 99 på ' + times[ind])
                             fail.append(times[ind])
        num_99 = 0
        for key in dict(sorted(all_codes.items())):
            error = ''
            #print(all_codes[key]['99'])
            if (all_codes[key]['99']):
                num_99 += 1
                error = ' - 99'
            print(key + ': ' + str(all_codes[key]['num']) +error ) #+ ': ' + all_codes[key]['99'])
        if (num_99 > 0):
            print('{} eneheter med 99-kode'.format(num_99))
        else:
            print('Ingen eneheter med 99-kode')

    def get_bonus_points(self):
        """Return bonus points configuration from config_poengo.py."""
        return poengo.bonus_points()

    def make_point_list(self):
        """
        Calculate PoengO (point orienteering) results with full scoring.

        PoengO Scoring Components:
        1. Control Points: Fixed points per control visited (e.g., 50 pts each)
        2. Bonus Points: Age/gender class handicap (from config_poengo.py)
        3. Bonus Tracks: Extra points for visiting control pairs in sequence
        4. Time Penalty: Points deducted for exceeding max time
        5. Climb Competition: Separate ranking on climb track with bonus points
        6. Sprint Competition: Separate ranking on sprint track with bonus points

        Special handling:
        - If climb winner is also sprint winner, swap 1st/2nd place sprint points
        - Ties in climb/sprint share same points
        - DSQ runners can still score in PoengO (tag changed to 'inne')

        Returns:
            List of runner dictionaries sorted by total points (descending)
        """
        # Initialize scoring parameters from config_poengo.py
        self.heading = ['Plass','Navn', 'Klubb','Tid']
        climb_time = ''
        sprint_time = ''
        climbers = []
        sprinters = []
        data = poengo.data
        maxtime = poengo.data()['maxtime']                      # Max time before penalties (e.g., 40 min)
        overtime_penalty = poengo.data()['overtime_penalty']    # Points deducted per minute over (e.g., 35 pts)
        control_point = poengo.data()['control_point']          # Points per control (e.g., 50 pts)
        race_controls = poengo.data()['race_controls']          # Valid controls per course
        climb_point = poengo.data()['climb_point']              # Prize points for climb (e.g., [200,100,50])
        sprint_point = poengo.data()['sprint_point']            # Prize points for sprint (e.g., [100,75,50])
        race_courses = poengo.courses()                         # Maps classes to course types
        bonus_tracks = poengo.data()['bonus_tracks']            # "103->130 108->73" format
        bonus_tracks = bonus_tracks.split()
        bonus_tracks.sort()
        climb_track = poengo.data()['climb_track']              # Controls defining climb (e.g., ['103','130'])
        sprint_track = poengo.data()['sprint_track']            # Controls defining sprint (e.g., ['108','73'])

        # Build heading columns dynamically based on config
        if (len(sprint_track) > 0):
            self.heading.extend(['Sprint', 'sprintsek'])
        if (len(climb_track) > 0):
            self.heading.extend(['Klatrestrekk', 'klatresek'])
        self.heading.extend(['Poengsum','Postpoeng','Strekkpoeng','Ekstrapoeng','Bonuspoeng','Tidstraff'])

        self.get_names()
        names = self.runners
        results = []
        all_controls=(race_controls['All'].split())
        all_controls.sort(key=int)
        self.heading.extend(all_controls)  # Add individual control columns
        self.heading.extend(bonus_tracks)  # Add bonus track columns
        # Process each runner
        for name in names:
            if(name[11] != None):  # name[11] = control codes with timestamps

                # Initialize scoring variables for this runner
                sprint_time = ''
                climb_time = ''
                sprint_lap =  10000  # Invalid time sentinel
                climb_lap =  10000   # Invalid time sentinel
                sum_points = 0
                time_penalty = 0
                control_points = 0
                track_points = 0
                climb_points = 0
                bonus = 0

                text = self.set_runner_details(name)
                text['Tid'] = name[8]
                text['tag'] = self.set_tag(name[10])
                race_class = text['Klasse']

                # name[11] format: "101 245, 103 312," (code timestamp,)
                codesandtimes = name[11].split()
                course = race_courses[race_class]  # Get course type for this class
                course_controls = race_controls[course]
                course_controls = course_controls.split()

                if text['Tid']:
                    controls= list(text['Poster'].split())  # Controls visited by runner
                    # Filter out special codes
                    controls = [x for x in controls if x != '99']   # Control unit error
                    controls = [x for x in controls if x != '250']  # Special marker
                    # Start with negative control point since finish is included in sprint
                    control_points =  - control_point
                    text['Poster'] = controls

                    # Award points for each course control visited
                    for code in course_controls:
                        if code in controls:
                            text[code] = control_point
                            control_points = control_points + control_point
                        else:
                            text[code] = str('')

                    sum_points = control_points

                    # Calculate time penalty if over max time
                    overtime = text['Tid'] - timedelta(minutes=maxtime)
                    if overtime.days == 0:  # Finished on same day
                        # Penalty = minutes over * penalty per minute (negative)
                        time_penalty= math.ceil(overtime.seconds / 60) * - overtime_penalty
                        sum_points = sum_points + time_penalty

                    # Add class-based bonus points
                    try:
                        bonus=poengo.bonus_points()[text['Klasse']]
                        sum_points = sum_points + bonus
                    except Exception:
                        text['Bonus']=str('')
                    # Process bonus tracks (control pairs worth extra points)
                    try:
                        tracks = poengo.bonus_track()[text['Klasse']]
                        # Initialize all track columns to empty
                        for track in bonus_tracks:
                            text[track] = str('')

                        # Helper function to calculate lap time between two controls
                        def calculate_lap_time(ctrl1, ctrl2, codes_times, start_idx):
                            """
                            Extract lap time from codesandtimes string.

                            Args:
                                ctrl1, ctrl2: Control codes
                                codes_times: List of codes and times
                                start_idx: Index to start searching from (for handling duplicates)

                            Returns:
                                Tuple of (lap_seconds, formatted_time_string)
                            """
                            # Find the occurrence of ctrl1 at or after start_idx
                            i1 = codes_times.index(ctrl1, start_idx * 2) + 1  # *2 because codes_times has "code, time, code, time"
                            i2 = codes_times.index(ctrl2, i1) + 1
                            t1 = int(codes_times[i1][:-1])  # Remove trailing comma
                            t2 = int(codes_times[i2][:-1])
                            lap_seconds = t2 - t1
                            minutes, seconds = divmod(lap_seconds, 60)
                            return lap_seconds, f'{minutes:02d}:{seconds:02d}'

                        # Check each bonus track for this class
                        for track in tracks:
                            # track format: [start_control, end_control, points]
                            # Ensure points is an integer (config might return strings)
                            start_ctrl, end_ctrl, points = str(track[0]), str(track[1]), int(track[2])

                            if start_ctrl in controls and end_ctrl in controls:
                                # Find ALL occurrences of both controls
                                # Check if ANY consecutive pair exists (handles multiple visits)
                                track_found = False

                                for i in range(len(controls) - 1):
                                    # Check if this position and next form the bonus track
                                    if controls[i] == start_ctrl and controls[i+1] == end_ctrl:
                                        # Found consecutive bonus track!
                                        track_points += points
                                        text[f"{start_ctrl}->{end_ctrl}"] = points
                                        track_found = True

                                        try:
                                            # Calculate climb lap time if this is the climb track
                                            if start_ctrl in climb_track and end_ctrl in climb_track:
                                                climb_lap, climb_time = calculate_lap_time(
                                                    start_ctrl, end_ctrl, codesandtimes, i
                                                )

                                            # Calculate sprint lap time if this is the sprint track
                                            if start_ctrl in sprint_track and end_ctrl in sprint_track:
                                                sprint_lap, sprint_time = calculate_lap_time(
                                                    start_ctrl, end_ctrl, codesandtimes, i
                                                )
                                        except (ValueError, IndexError):
                                            # Timestamp extraction failed, but track points already awarded
                                            pass

                                        # Only count the track once even if visited multiple times
                                        break

                        sum_points = sum_points + track_points
                    except KeyError:
                        # Class not found in bonus_track() configuration
                        text['Strekkpoeng']=str('')
    
                    # Store all scoring components in result dictionary
                    text['sprintsek'] = sprint_lap      # Numeric for sorting
                    text['klatresek'] = climb_lap       # Numeric for sorting
                    text['Klatrestrekk'] = climb_time   # Display string
                    text['Sprint'] = sprint_time        # Display string
                    text['Poengsum'] = sum_points
                    text['Bonuspoeng']= bonus
                    text['Tidstraff'] = time_penalty
                    text['Postpoeng'] = control_points
                    text['Strekkpoeng'] = track_points
                    text['Tid'] = str(text['Tid'])
                    text['Ekstrapoeng'] = str('')
                    result = []
                    results.append(text)

        # Award prizes for climb and sprint competitions
        if len(results) < 3:
            diff = len(results) + 1
        else:
            diff = 0 

        # Climb Competition: Award bonus points to top 3 fastest climbers
        if len(climb_track) > 0 and len(results) > 0:
            results = sorted(results, key=lambda tup: tup['klatresek'])
            vinner = results[0]['Navn']  # Save climb winner for sprint logic

            forrige_tid = None
            poeng_index = 0
            plass_teller = 0
            siste_poengplass = 3  # Only top 3 places get points

            for i in range(len(results)):
                tid = results[i]['klatresek']
                if tid == 10000:
                    continue  # Invalid time (didn't complete climb track)

                # New placement if different time
                if tid != forrige_tid:
                    plass_teller += 1

                    # Stop after awarding points to top 3 unique times
                    if plass_teller > siste_poengplass:
                        break

                    # Get points for this placement
                    if poeng_index < len(climb_point):
                        poeng = climb_point[poeng_index]  # e.g., [200, 100, 50]
                    else:
                        poeng = 0
                else:
                    # Same time as previous = same points (tie)
                    poeng = climb_point[poeng_index - 1]
                    siste_poengplass -= 1  # Adjust remaining point slots

                poeng_index += 1
                # Add climb points to total score
                results[i]['Poengsum'] += poeng
                try:
                    results[i]['Ekstrapoeng'] = str(int(results[i]['Ekstrapoeng']) + poeng)
                except ValueError:
                    results[i]['Ekstrapoeng'] = poeng

                forrige_tid = tid
        # Add climb placement to display string
        plass = 1
        forrige_tid = None
        like_tider = 0  # Count runners sharing same time

        for result in results:
            tid = result.get('Klatrestrekk', '')
            if tid == '':
                continue

            if tid == forrige_tid:
                # Same time as previous = same placement (tie)
                result['Plass'] = plass
                like_tider += 1
            else:
                # New time = jump ahead by number of tied times
                plass = plass + like_tider
                result['Plass'] = plass
                like_tider = 1

            forrige_tid = tid
            # Append placement to display string: "03:45 (2)"
            result['Klatrestrekk'] = f"{tid} ({result['Plass']})"

        # Sprint Competition: Award bonus points to top 3 fastest sprinters
        if (len(sprint_track) > 0 and len(results) > 0):
            results = sorted(results, key=lambda tup: tup['sprintsek'])

            # Special rule: If climb winner also wins sprint, swap 1st/2nd place points
            # This prevents one person from dominating both competitions
            if (results[0]['Navn'] == vinner):
                sprint_point = ([sprint_point[1],sprint_point[0],sprint_point[2]])  # Swap positions 0 and 1

        # Award sprint points (same logic as climb)
        if len(sprint_point) > 0 and len(results) > 0:
            results = sorted(results, key=lambda tup: tup['sprintsek'])

            forrige_tid = None
            poeng_index = 0
            plass_teller = 0
            siste_poengplass = 3  # Only top 3 places get points

            for i in range(len(results)):
                tid = results[i]['sprintsek']
                if tid == 10000:
                    continue  # Invalid time (didn't complete sprint track)

                if tid != forrige_tid:
                    plass_teller += 1

                    if plass_teller > siste_poengplass:
                        break

                    if poeng_index < len(sprint_point):
                        poeng = sprint_point[poeng_index]  # e.g., [100, 75, 50]
                    else:
                        poeng = 0
                else:
                    # Tie - same points as previous
                    poeng = sprint_point[poeng_index - 1]
                    siste_poengplass -= 1

                poeng_index += 1
                results[i]['Poengsum'] += poeng
                try:
                    results[i]['Ekstrapoeng'] = str(int(results[i]['Ekstrapoeng']) + poeng)
                except ValueError:
                    results[i]['Ekstrapoeng'] = poeng

                forrige_tid = tid

        # Add sprint placement to display string
        plass = 1
        forrige_tid = None
        like_tider = 0

        for result in results:
            tid = result.get('Sprint', '')
            if tid == '':
                continue

            if tid == forrige_tid:
                result['Sprint'] = f"{tid} ({plass})"
                like_tider += 1
            else:
                plass = plass + like_tider
                result['Sprint'] = f"{tid} ({plass})"
                like_tider = 1

            forrige_tid = tid

        # Final sort by total points (highest first)
        results = sorted(results, key=lambda tup: (tup['Poengsum']) , reverse=True)

        # Assign final placements
        plass = 1
        point = ''
        for result in results:
            if (result['Poengsum'] == point):
                # Tie - keep showing same point total
                result['Poengsum'] = point
            else:
                result['Plass'] = plass
            plass +=1
            point = result['Poengsum']
            # DSQ runners can still score in PoengO
            if result['tag'] == 'dsq':
                result['tag'] = 'inne'

        return results

    def make_finish_list(self):
        """
        Placeholder for finish list generation.
        Currently not implemented.
        """
        print('Hello')

    def set_poengo_text(self,name):
        """
        Filter PoengO result dictionary to only fields needed for treeview display.

        Excludes internal fields like individual control columns and lap times.
        """
        keys_to_treeview = {'Startnr','Plass','Navn','Tid','Sprint','Klatrestrekk','Poengsum','Postpoeng','Strekkpoeng','Ekstrapoeng','Bonuspoeng','Tidstraff','tag'}
        return {key: name[key] for key in keys_to_treeview}

    def set_runner_details(self, name):
        """
        Convert database runner tuple to dictionary with readable field names.

        Maps database fields (name[0], name[2], etc.) to named dictionary keys.
        See module docstring for field index mappings.

        Args:
            name: Runner tuple from database

        Returns:
            Dictionary with runner details
        """
        text = {
                'id' : name[0],
                'Startnr': str(name[7]), 
                'Plass':str(''),
                'Navn': name[2],
                'Klubb': name[3],
                'Tid': str(name[8]),
                'Time': name[8],
                'Differanse':str(''),
                'Klasse':self.find_class_name(name[4]),
                'Starttid':str(''),
                'tag':name[10],
                'Brikkenr':str(name[6]),
                'Poeng':str(''),
                'Poster': name[17],
                'Innkomst': name[12],
                'Times' : name[11], # Koder, tid og 99
                'Starttime' : name[14], # denne bør brukes i hele programmet i stedet for Starttid
                'Invoice' : name[24], # Brukes i xml eksport
                'Courseid' : name[16] 
                 }
         # Disse under brukes kun hvis det blir krøll over
        if name[14]: #Sjekker at løper har startid
            text['Starttid']= str(name[14].strftime('%H:%M'))
        if not text['Startnr'] or text['Startnr'] == "None": # Bruker "None" siden jeg har brukt str(name[7]) over
            text['Startnr'] = ' '
        if not text['Brikkenr']:
            text['Brikkenr'] = ' '
        if not text['Starttid']:
            text['Starttid'] = ''

        return text

    def check_inn_time(self, inntime):
        """
        Check if runner finished within last minute (for highlighting).

        Args:
            inntime: Finish arrival timestamp

        Returns:
            'last' if finished within 1 minute, otherwise 'inne'
        """
        if inntime:
            if (datetime.now() + timedelta(minutes=-1) <= inntime):
                return 'last'
            else:
                return 'inne'

    def get_time(self, starttime):
        """
        Calculate elapsed time for runner still out in forest.

        Args:
            starttime: When runner started (datetime)

        Returns:
            Timedelta of elapsed time, or None if not started
        """
        spurt = 0
        if starttime:
            if (datetime.now() - starttime).days >= 0:
                now = time.strftime('%H:%M:%S')
                fmt = '%H:%M:%S'
                atime = datetime.strptime(now, fmt) - timedelta(0, abs(spurt))
                tdelta = atime - starttime
                return (abs(timedelta(days=tdelta.days))+tdelta)

        return None

    def set_tag(self, tag):
        """
        Convert database status code to display tag.

        Status codes from Brikkesys:
            I = In forest (ute)
            A = Arrived/finished (inne)
            D = Disqualified (dsq)
            N = Did not start (dns)
            X = Organizer (arr)
            E = Abandoned (dns)
            H = Started (ute)
            C = Restart (ute)
            P = Confirmed time (inne)
            V = (dns)
        """
        if tag == 'I':
            return 'ute'
        elif tag == 'A':
            return 'inne'
        elif tag == 'D':
            return 'dsq'
        elif tag == 'N':
            return 'dns'
        elif tag == 'X':
            return 'arr'
        elif tag == 'E': #Brutt
            return 'dns'
        elif tag == 'H': #Startet
            return 'ute'
        elif tag == 'C': #Omstart
            return 'ute'
        elif tag == 'P': #Bekreftet tid
            return 'inne'
        elif tag == 'V': 
            return 'dns'
        else:
            self.log_file.write("Cannot find tag {0}: \n".format(str(tag)))
            self.log_file.flush()

    def make_prewarn_list_2(self, pre_db):
        """
        Generate prewarn list from separate prewarn database.

        Alternative prewarn system using dedicated database instead of
        Brikkesys online controls.

        Args:
            pre_db: Database connection to prewarn database

        Returns:
            List of runners who have registered at prewarn checkpoints
        """
        prewarn_list = []
        prewarn_runners = self.get_prewarn_runners(pre_db)
        for runner in prewarn_runners:
            runner = list(runner)
            runner[10] = self.set_tag(runner[10])

            if runner[10] == 'ute':
                try:
                    runner[8] = self.get_time(runner[14])
                except:
                    if runner[10] == 'dns':
                        runner[8] = 'DNS'
            if not runner[8]:
                runner[8] = runner[10]
            prewarn_list.insert(0, self.set_runner_details(runner))
        return prewarn_list

    def get_prewarn_runners(self, pre_db):
        """
        Fetch runners from prewarn database by start number.

        Reads start numbers incrementally from prewarn database
        and matches them to runners in main race database.

        Args:
            pre_db: Database connection to prewarn database

        Returns:
            List of runner tuples
        """
        nums = pre_db.read_start_numbers()
        runners = []
        for num in nums:
            if self.idx < num[0]:
                self.idx = num[0]
                try:
                    start_num = int(num[1])
                    runner = self.find_runner(start_num)
                    if runner:
                        runners.append(runner)
                except:
                    str_num = num
                    self.log_file.write("No startnumbers {0}: \n".format(str(num)))
                    self.log_file.flush()
        return runners


