#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql.cursors
import config

# Connect to the database on speaker pc
connection = pymysql.connect(**config.get_config('prewarn'))
stop = False

with connection.cursor() as cursor:
    sql= "DELETE FROM startnumbers"
    cursor.execute(sql)
    connection.commit()
    while not stop:
        value = input()
        if value == 'stop':
            stop = True
        else:

            # Create a new record
            sql = "INSERT INTO startnumbers (numbers) VALUES (%s)"
            cursor.execute(sql, (value))
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            sql = " SELECT * FROM startnumbers"
            cursor.execute(sql)
            #print(cursor.fetchall())
            connection.commit()

    sql= "DELETE FROM startnumbers"
    cursor.execute(sql)
    connection.commit()
    connection.close() 
