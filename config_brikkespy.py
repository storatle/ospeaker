#!/usr/bin/env python3

def no_time_classes():
    return [
            'N-åpen'
            ]

def unranked_classes():
    return [
            'D 9-10',
            'H 9-10',
            'N-åpen 9-20'
            ]

def course_id(name):
    if name == "": 
        return "AK"
        

def drop_diskcheck(name):
    if name == "":
        return False
