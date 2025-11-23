#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Race Diagnostics Utility for BrikkeSpy/OSpeaker

This standalone script provides diagnostic tools for analyzing race data,
specifically focusing on control unit failures and disqualification analysis.

Primary Functions:
    1. Control Unit Failure Detection (99-codes):
       - Identifies control units that malfunctioned during the race
       - A '99' code indicates a control unit failed to register properly
       - Helps race organizers identify faulty equipment

    2. Disqualification Analysis:
       - Examines why runners were disqualified
       - Compares punched controls vs. required course controls
       - Identifies which controls caused the most disqualifications

Usage:
    # Check specific race number on specific server
    python status.py --race 246 --server local

    # Use defaults (race 246 on local server)
    python status.py

    # Check different race on remote server
    python status.py --race 250 --server Milo

Command-line Arguments:
    --race, -r     : Race number to analyze (default: 246)
    --server, -s   : Database server name (default: 'local')
    --check-disk   : Run disqualification analysis (default: enabled)
    --check-99     : Run control unit failure check (default: enabled)

Note:
    This is a diagnostic tool primarily used during/after race events.
    The main GUI application provides access to make_99_list() via
    File → Status menu, but not to check_disk_reason().
"""

import argparse
from brikkesys import Database
from orace import Race
import config_brikkespy as config


def main():
    """
    Main entry point for race diagnostics script.

    Parses command-line arguments and runs requested diagnostic checks
    on the specified race.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Run diagnostics on orienteering race data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python status.py                        # Run all checks on race 246 (local)
  python status.py -r 250                 # Check race 250
  python status.py -r 248 -s Milo         # Check race 248 on Milo server
  python status.py -r 246 --no-check-disk # Only check control units (no DSQ analysis)
        """
    )

    parser.add_argument(
        '-r', '--race',
        type=int,
        default=246,
        help='Race number to analyze (default: 246)'
    )

    parser.add_argument(
        '-s', '--server',
        type=str,
        default='local',
        help="Database server name: 'local', 'Milo', 'Klara' (default: 'local')"
    )

    parser.add_argument(
        '--no-check-disk',
        action='store_true',
        help='Skip disqualification analysis'
    )

    parser.add_argument(
        '--no-check-99',
        action='store_true',
        help='Skip control unit failure check'
    )

    args = parser.parse_args()

    # Connect to database
    print(f"Connecting to database: {args.server}")
    db = Database(args.server)

    # Load race data
    print(f"Loading race number: {args.race}")
    race = Race(db, args.race)

    print()

    # Run disqualification analysis
    if not args.no_check_disk:
        print("=" * 70)
        print("DISQUALIFICATION ANALYSIS")
        print("=" * 70)
        race.check_disk_reason()
        print()

    # Run control unit failure check
    if not args.no_check_99:
        print("=" * 70)
        print("CONTROL UNIT FAILURE CHECK (99-codes)")
        print("=" * 70)
        race.make_99_list()
        print()

    print("Diagnostics complete.")


if __name__ == "__main__":
    main()
