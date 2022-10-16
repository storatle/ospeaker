#!/usr/bin/env python3

def no_time_classes():
    return [
            'N-åpen'
            ]

def unranked_classes():
    return [
            'D 9-10',
            'H 9-10',
            'N-åpen 10-20'
            ]

def course_id(name):
    if name == "Magnus Landstad": 
        return "AK"
        

def drop_diskcheck(name):
    if name == "":
        return False
