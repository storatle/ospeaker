#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
list_controls.py - Display control codes found by each runner

Simple utility to show which controls each runner has punched.
Displays: Start Number, Name, Class, and all Control Codes found.

Usage:
    python list_controls.py [server]

Arguments:
    server: Database server (local, Klara, Milo) or IP address. Default: local

Example:
    python list_controls.py local
    python list_controls.py Milo
"""

import sys
from brikkesys import Database


def get_runner_controls_data(db, race_idx):
    """
    Get runner controls data for GUI display.

    Args:
        db: Database connection
        race_idx: Index of race to display

    Returns:
        Tuple of (race_name, runner_list) where runner_list contains
        dictionaries with 'start_num', 'name', 'class', 'controls'
    """
    selected_race = db.races[race_idx]
    race_id = selected_race[0]
    race_name = selected_race[1]

    # Read classes for this race
    db.read_classes(race_id)
    class_map = {}
    for cls in db.classes:
        if cls[14] == 0:  # Only actual classes (not courses)
            class_map[cls[0]] = cls[1]

    # Read all runners for this race
    runners = db.read_names(race_id)

    if not runners:
        return race_name, []

    # Sort runners by class name and then by start number
    def get_sort_key(runner):
        class_id = runner[4]
        class_name = class_map.get(class_id, "Unknown")
        start_num = runner[7] if runner[7] else 0
        return (class_name, start_num)

    runners = sorted(runners, key=get_sort_key)

    # Build result list
    result_list = []
    for runner in runners:
        start_num = runner[7] if runner[7] else ""
        name = runner[2]
        class_id = runner[4]
        class_name = class_map.get(class_id, "Unknown")
        controls = runner[17] if runner[17] else ""

        # Format controls as a space-separated list
        if controls:
            control_list = controls.split()
            controls_display = " ".join(control_list)
        else:
            controls_display = "(no controls)"

        result_list.append({
            'start_num': str(start_num),
            'name': name,
            'class': class_name,
            'controls': controls_display
        })

    return race_name, result_list


def display_runner_controls(ip_address='local'):
    """
    Connect to database and display controls found by each runner.

    Args:
        ip_address: Database server identifier
    """
    # Connect to database
    print(f"Connecting to database: {ip_address}")
    db = Database(ip_address)

    # Check if races are available
    if not db.races:
        print("No races found in database.")
        return

    # Display available races
    print("\nAvailable races:")
    for idx, race in enumerate(db.races):
        race_date = race[2].strftime("%d-%m-%Y") if race[2] else "No date"
        print(f"  {idx}: {race[1]} ({race_date})")

    # Select race (use first race by default, or prompt user)
    race_idx = 0
    if len(db.races) > 1:
        try:
            race_idx = int(input(f"\nSelect race (0-{len(db.races)-1}): "))
        except (ValueError, EOFError):
            print("Using first race...")

    selected_race = db.races[race_idx]
    race_id = selected_race[0]
    race_name = selected_race[1]

    print(f"\n{'='*80}")
    print(f"Race: {race_name}")
    print(f"{'='*80}\n")

    # Read classes for this race
    db.read_classes(race_id)
    class_map = {}
    for cls in db.classes:
        if cls[14] == 0:  # Only actual classes (not courses)
            class_map[cls[0]] = cls[1]

    # Read all runners for this race
    runners = db.read_names(race_id)

    if not runners:
        print("No runners found for this race.")
        return

    # Sort runners by class name and then by start number
    def get_sort_key(runner):
        class_id = runner[4]
        class_name = class_map.get(class_id, "Unknown")
        start_num = runner[7] if runner[7] else 0
        return (class_name, start_num)

    runners = sorted(runners, key=get_sort_key)

    # Display header
    print(f"{'Start#':<8} {'Name':<25} {'Class':<12} {'Controls Found'}")
    print(f"{'-'*8} {'-'*25} {'-'*12} {'-'*40}")

    current_class = None
    runner_count = 0

    # Display each runner and their controls
    for runner in runners:
        start_num = runner[7] if runner[7] else ""
        name = runner[2]
        class_id = runner[4]
        class_name = class_map.get(class_id, "Unknown")
        controls = runner[17] if runner[17] else ""

        # Add class separator for readability
        if class_name != current_class:
            if current_class is not None:
                print()  # Blank line between classes
            current_class = class_name

        # Format controls as a space-separated list
        if controls:
            # Convert to list and back to clean up spacing
            control_list = controls.split()
            controls_display = " ".join(control_list)
        else:
            controls_display = "(no controls)"

        print(f"{str(start_num):<8} {name:<25} {class_name:<12} {controls_display}")
        runner_count += 1

    print(f"\n{'-'*80}")
    print(f"Total runners: {runner_count}")


def main():
    """Main entry point."""
    # Parse command line arguments
    server = 'local'
    if len(sys.argv) > 1:
        server = sys.argv[1]

    try:
        display_runner_controls(server)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
