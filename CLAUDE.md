# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

BrikkeSpy/OSpeaker is a Python3 application for reading and displaying orienteering race results from Brikkesys databases. It provides real-time monitoring of runners, result displays, pre-warnings, and specialized scoring for PoengO (point orienteering) competitions.

## Running the Application

### Main Entry Point
```bash
python brikkespy.py [server] [options]
```

Arguments:
- `server`: Database server name (local, Klara, Milo) or IP address. Default: local
- `-f, --finish`: Display finish list view
- `-pre, --prewarn`: Enable online prewarn system from database
- `-p, --poengo`: Enable PoengO scoring mode
- `-v, --ovirus`: Enable O-Virus mode

### Examples
```bash
python brikkespy.py local              # Run with local database
python brikkespy.py Milo -p            # Connect to Milo server with PoengO mode
python brikkespy.py local -f -pre      # Local with finish list and prewarn
```

### Standalone Scripts
```bash
python plotbonuspoeng.py               # Plot bonus points bar chart for PoengO classes
```

## Required Dependencies

Install dependencies in this order:
```bash
sudo apt-get install python3-tk        # tkinter for GUI
pip3 install pymysql                   # MySQL database connector
sudo pip3 install PyPDF2               # PDF generation
sudo pip3 install reportlab            # PDF rendering
pip3 install pillow                    # PIL for image handling
pip install screeninfo                 # Screen resolution detection
pip install matplotlib                 # For plotting bonus points
```

## Architecture

### Core Application Flow
1. **brikkespy.py** - Entry point, parses arguments and launches GUI
2. **ospeakerui.py** - Main GUI application (Window and Tab classes)
3. **brikkesys.py** - Database abstraction layer (Database class)
4. **orace.py** - Race data model and business logic (Race class)

### Key Classes

**Database (brikkesys.py)**
- Handles all MySQL database connections and queries
- Reads races, runners (names), classes, online controls, and eventor data
- Writes logs to `/var/log/ospeaker.log` (Linux) or `ospeaker.log` (Windows)
- Connection parameters configured in `config_database.py`

**Race (orace.py)**
- Core business logic for race data processing
- Key methods:
  - `make_result_list(class_name)` - Generate result list for a class
  - `make_start_list(class_name)` - Generate start list
  - `make_last_list()` - Show most recent finishers
  - `make_prewarn_list()` - Process online control prewarn data
  - `make_point_list()` - Calculate PoengO scores with bonus tracks and time penalties
  - `make_99_list()` - Diagnostic tool for checking control unit failures
  - `check_disk_reason()` - Analyze disqualifications and missing controls

**Window and Tab (ospeakerui.py)**
- Tkinter-based GUI with notebook tabs
- Tab types: 'adm' (administration), 'results', 'prewarn', 'poengo', 'finish'
- Auto-refresh mechanisms using `.after()` callbacks
- Full-screen display optimized for race speaker screens

### Runner Status Tags
Runners have status tags that determine display and scoring:
- `I` → 'ute' (out in forest)
- `A` → 'inne' (finished)
- `D` → 'dsq' (disqualified)
- `N` → 'dns' (did not start)
- `X` → 'arr' (organizer)
- `E` → 'dns' (abandoned)
- `H` → 'ute' (started)
- `P` → 'inne' (confirmed time)

### PoengO Scoring System

PoengO is a points-based orienteering format with:
- Control points: 50 points per control
- Bonus points by age class (configured in `config_poengo.py`)
- Bonus tracks: Extra points for visiting specific control sequences
- Time penalty: Points deducted for exceeding max time (35 points/minute)
- Climb and sprint competitions with separate rankings

**Score Calculation Flow:**
1. Load race controls and bonus tracks from `config_poengo.py`
2. Award control points for each visited control
3. Add bonus points based on runner's age class
4. Add track points for completing bonus track sequences
5. Calculate climb/sprint lap times and award top-3 prizes
6. Apply time penalties if over max time
7. Handle ties in climb/sprint competitions

**Configuration (config_poengo.py):**
- `bonus_points()` - Points by age class
- `bonus_track()` - Track sequences with point values
- `courses()` - Map classes to course types
- `data()` - Max time, control points, penalties, climb/sprint tracks

## Configuration Files

### Database Configuration (config_database.py)
Database connection parameters for different servers:
- 'local': Local MySQL (127.0.0.1)
- 'Milo': Remote race PC
- 'Klara': Another remote PC
- 'Prewarn': Local prewarn database

### Race-Specific Configuration (config_brikkespy.py)
- `no_time_classes()`: Classes showing only "fullført" instead of times
- `unranked_classes()`: Classes without ranking/placement
- `course_id(name)`: Override course ID for specific runners
- `drop_diskcheck(name)`: Skip disqualification analysis for specific runners

### PoengO Configuration (config_poengo*.py)
Multiple config files exist for different events:
- `config_poengo.py` - Default configuration
- `config_poengo_klubbm.py` - Club championship settings
- `config_poengo_lommelykt.py` - Flashlight event settings

**Dynamic Config Loading:** `orace.py` checks current working directory first, then script directory for `config_poengo.py`

## Output Generation

### PDF Generation (pdfgen.py)
- Start lists and result lists
- Page breaks configurable
- Options for single class or all classes
- Accessible via GUI menu: File → PDF

### XML Export (xmlgen.py)
- IOF XML 3.0 format result lists
- Includes event metadata, race data, and eventor integration
- Accessible via GUI menu: File → XML

### CSV Export
- PoengO results can be exported to `resultater.csv`
- Includes all control codes and bonus track columns

## GUI Structure

### Tabs
- **Administrasjon**: Split view showing finished runners (top) and runners still out (bottom) for selected class
- **Resultater**: Three display modes via buttons:
  - Klassevis: Cycle through each class
  - Loop: Continuous scroll of all results
  - Siste: Show most recent finishers
- **Forvarsel**: Online control warnings showing runners approaching checkpoints
- **Poeng-O**: PoengO results with scoring breakdown, includes plot button for bonus points visualization
- **Målliste**: Chronological finish list across all classes

### Menu Options
- **File → Status**: Run diagnostic check for control unit failures (99-codes)
- **PDF → Lag startliste**: Generate PDF start list
- **PDF → Lag resultatliste**: Generate PDF results
- **XML → Lag resultatliste**: Export IOF XML results

## Database Schema Notes

The application reads from Brikkesys MySQL database tables:
- `RACES/races`: Race definitions
- `NAMES/names`: Runner registrations (name[0]=id, name[2]=name, name[6]=ecard, name[7]=startnum, name[8]=time, name[10]=status, name[11]=codes+times, name[17]=codes_only)
- `CLASSES/classes`: Class definitions (row[14] determines if course or class)
- `ONLINECONTROLS/onlinecontrols`: Online control punch data for prewarn
- `invoicelevels`: Invoice/fee levels for XML export
- `eventor_personid`, `eventor_clubs`: Eventor integration data

Case sensitivity varies by database - queries try uppercase first, then lowercase.

## Network Setup

To connect to remote Brikkesys PC:
1. On Brikkesys PC: Disable public network firewall, find IP with `ipconfig`
2. On BrikkeSpy PC (Linux): Set network to "Link-Local Only" in IPv4 settings
3. Verify connection with `ping` to Brikkesys PC IP address
4. Update server IP in `config_database.py`

## Platform Differences

Windows vs Linux paths:
- Log file: `ospeaker.log` (Windows) vs `/var/log/ospeaker.log` (Linux)
- Banner image: `C:\Program Files (x86)\Brikkespy\images\black_MILO_banner.png` (Windows) vs `/etc/black_MILO_banner.png` (Linux)
- Platform detection: `sys.platform == "win32"`

## Common Development Tasks

### Adding a New Race Server
1. Add configuration in `config_database.py` `get_config()` function
2. Connection requires: host, user, passwd, db, charset

### Modifying PoengO Scoring Rules
1. Edit `config_poengo.py` to adjust bonus points, time limits, or bonus tracks
2. For event-specific rules, create a new `config_poengo_eventname.py` file
3. Place config in working directory to override default

### Debugging Race Results
- Use File → Status menu to check for control unit failures (99-codes)
- Check `/var/log/ospeaker.log` for database errors
- Use `check_disk_reason()` to analyze disqualifications
- Control code 99 indicates a unit malfunction during runner's punch
