#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='Purcell18',
                             db='startnummerdatabase',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

stop = False

with connection.cursor() as cursor:
    sql= "DELETE FROM startnumbers"
    cursor.execute(sql)
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
            print(cursor.fetchall())
            connection.commit()
