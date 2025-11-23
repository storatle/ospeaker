#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IOF XML 3.0 Result List Generator for BrikkeSpy/OSpeaker

This module generates XML result files in IOF XML 3.0 format (International
Orienteering Federation standard) for uploading to national federation systems
like Eventor (Norwegian Orienteering Federation).

The generated XML includes:
    - Event metadata (name, date)
    - Class results for all race classes
    - Runner details (name, club, Eventor IDs)
    - Result data (times, status, split times)
    - Fee/invoice information

Output Format:
    IOF XML 3.0 specification: http://www.orienteering.org/datastandard/3.0

Usage:
    From GUI: File → XML → Lag resultatliste
    From code:
        >>> xml_gen = xml()
        >>> xml_gen.result_list(db, race_number)

Output:
    Creates 'result.xml' in current directory
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from orace import Race
import decimal as dec


class xml:
    """
    IOF XML 3.0 result list generator.

    Generates standardized XML files for orienteering race results
    compatible with international federation systems (Eventor, etc.).
    """

    def __init__(self):
        """Initialize XML generator."""
        print("XML generator")


    def add_XMLNS_attributes(self, tree, xmlns_uris_dict):
        """
        Add XML namespace attributes to root element.

        XML namespaces define the schema locations for validation.
        Required for IOF XML 3.0 compliance.

        Args:
            tree (Element or ElementTree): XML tree or root element
            xmlns_uris_dict (dict): Namespace prefix to URI mapping
                Example: {'xsd': 'http://www.w3.org/2001/XMLSchema'}

        Side Effects:
            Modifies tree element by adding xmlns:prefix attributes
        """
        # Get root element if passed an ElementTree
        if not ET.iselement(tree):
            tree = tree.getroot()

        # Add each namespace as an attribute
        for prefix, uri in xmlns_uris_dict.items():
            tree.attrib['xmlns:' + prefix] = uri


    def result_list(self, db, race_number):
        """
        Generate IOF XML 3.0 result list for a race.

        Creates complete XML document with event metadata, class results,
        runner details, split times, and fee information. Integrates with
        Eventor database for official person and club IDs.

        Args:
            db (Database): Database connection object
            race_number (int): Race ID to generate results for

        Output:
            Creates 'result.xml' file in current directory

        XML Structure:
            ResultList
            ├── Event (name, dates)
            └── ClassResult (one per class)
                ├── Class (class name)
                └── PersonResult (one per runner)
                    ├── Person (name, Eventor ID)
                    ├── Organisation (club, Eventor club ID)
                    └── Result (times, status, splits, fees)
        """
        # Load race data
        race = Race(db, race_number)

        # Load fee/invoice information for this race
        invoice_level = db.read_invoicelevel(race_number)

        # Time format for parsing (not currently used)
        fmt = '%H:%M:%S'

        # Define XML namespaces for IOF XML 3.0 compliance
        xmlns_uris = {
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Create root element with IOF XML 3.0 attributes
        root = ET.Element(
            "ResultList",
            iofVersion="3.0",
            xmlns='http://www.orienteering.org/datastandard/3.0',
            createTime=datetime.now().isoformat(),
            creator="Brikkespy",
            status="Complete"
        )

        # Add namespace attributes
        self.add_XMLNS_attributes(root, xmlns_uris)

        # Build Event section (race metadata)
        event = ET.SubElement(root, "Event")
        ET.SubElement(event, "Name").text = race.race_name

        # Event start date
        startTime = ET.SubElement(event, "StartTime")
        ET.SubElement(startTime, "Date").text = race.race_date.strftime('%Y-%m-%d')

        # Event end date (same as start for single-day events)
        endTime = ET.SubElement(event, "EndTime")
        ET.SubElement(endTime, "Date").text = race.race_date.strftime('%Y-%m-%d')

        # Process each class in the race
        for race_class in race.classes:
            # Create ClassResult element for this class
            classresult = ET.SubElement(root, "ClassResult")

            # Get results for this class
            results = race.make_result_list(race_class[1])

            # Add class name
            rclass = ET.SubElement(classresult, "Class")
            ET.SubElement(rclass, "Name").text = race_class[1]

            # Process each runner in the class
            for runner in results:
                # Look up Eventor person ID from database
                # Eventor IDs are required for official federation integration
                eventor_personid = db.read_eventor_personid(runner.get('id'))

                # If Eventor person ID exists, also get club information
                if eventor_personid:
                    eventor_club = db.read_eventor_club(eventor_personid[0][3])

                # Create PersonResult element for this runner
                personresult = ET.SubElement(classresult, "PersonResult")

                # Person section - runner identity
                person = ET.SubElement(personresult, "Person")

                # Add Eventor person ID if available
                if eventor_personid:
                    ET.SubElement(person, "Id").text = str(eventor_personid[0][2])

                # Split full name into family name (last word) and given name (rest)
                name = ET.SubElement(person, "Name")
                ET.SubElement(name, "Family").text = runner.get('Navn').split()[-1]
                ET.SubElement(name, "Given").text = runner.get("Navn").replace(
                    ' ' + runner.get('Navn').split()[-1], ''
                )

                # Organisation section - club information
                organisation = ET.SubElement(personresult, "Organisation")

                # Add Eventor club ID if available
                if eventor_personid:
                    ET.SubElement(organisation, "Id").text = str(eventor_personid[0][3])

                ET.SubElement(organisation, "Name").text = runner.get("Klubb")

                # Result section - race performance data
                result = ET.SubElement(personresult, "Result")

                # Bib number (start number)
                ET.SubElement(result, "BibNumber").text = runner.get('Startnr')

                # Start and finish times (only for runners who started)
                if runner.get('tag') != 'dns':
                    ET.SubElement(result, "StartTime").text = (
                        '' if runner.get("Starttime") is None
                        else runner.get('Starttime').isoformat()
                    )
                    ET.SubElement(result, "FinishTime").text = (
                        '' if runner.get("Innkomst") is None
                        else runner.get("Innkomst").isoformat()
                    )

                # Total time in seconds (IOF standard)
                try:
                    # Try to get time from timedelta object
                    ET.SubElement(result, "Time").text = str(
                        int(runner.get('Time').total_seconds())
                    )
                except:
                    # Fallback for non-timedelta time values
                    ET.SubElement(result, "Time").text = str(runner.get("Tid"))

                # Runner status mapping (Norwegian → IOF standard)
                if runner.get('tag') == 'inne':
                    ET.SubElement(result, "Status").text = "OK"
                if runner.get('tag') == 'dns':
                    ET.SubElement(result, "Status").text = "DidNotStart"
                if runner.get('tag') == 'dsq':
                    ET.SubElement(result, "Status").text = "Disqualified"

                # Split times - individual control punches
                # Format: "controlcode time, controlcode time, ..."
                times = (
                    '' if runner.get('Times') is None
                    else runner.get('Times').split(',')
                )

                # Process all controls except last two (finish and clear)
                for control in times[0:-2]:
                    # Skip control code 99 (indicates unit malfunction)
                    if control.split()[0] != '99':
                        split = ET.SubElement(result, "SplitTime")
                        ET.SubElement(split, "ControlCode").text = control.split()[0]
                        ET.SubElement(split, "Time").text = control.split()[1]

                # E-card number (brikkenummer)
                ET.SubElement(result, "ControlCard").text = runner.get("Brikkenr")

                # Fee information (entry fees)
                # Only include if invoice data exists for this race
                if invoice_level:
                    try:
                        # Find the invoice level for this runner
                        # Matches runner's invoice ID with invoice_level table
                        ind = [
                            el.index(runner.get("Invoice"))
                            for i, el in enumerate(invoice_level)
                            if runner.get("Invoice") in el
                        ][0]

                        person_level = invoice_level[ind]

                        # Add fee information
                        assignedfee = ET.SubElement(result, "AssignedFee")
                        fee = ET.SubElement(assignedfee, "Fee")
                        ET.SubElement(fee, "Name").text = person_level[3]

                        # Amount with currency
                        amount = ET.SubElement(fee, "Amount")
                        amount.set("currency", "NOK")
                        amount.text = str(person_level[5])

                    except:
                        # Invoice level not found for this runner
                        print('Invoice level id {} '.format(invoice_level[0][2]))

        # Create ElementTree and write to file
        tree = ET.ElementTree(root)
        file = "result.xml"

        # Write XML with UTF-8 encoding and XML declaration
        with open(file, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)

        print(f"XML result file created: {file}")
