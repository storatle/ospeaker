#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='user',
                             password='passwd',
                             db='start_num_db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

stop = False
f = open('num.txt', 'w+')

while not stop:
    value = input()
    if value == 'stop':
        stop = True
    else:
        f.write(value + ';')
        f.flush()
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `startnumbers` (`number`) VALUES (%s)"
            cursor.execute(sql, (value))
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

# Henter alle løp
def read_numbers(self):
    sql = " SELECT * FROM startnumbers"
    try:
        # Execute the SQL command
        self.cursor.execute(sql)
        # Fetch all the rows in a list of lists.
        self.races = self.cursor.fetchall()

    except Exception:
        sql = " SELECT * FROM races"
        self.cursor.execute(sql)
        self.races = self.cursor.fetchall()

    except:
        print("Error: unable to fecth data")