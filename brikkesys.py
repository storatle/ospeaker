#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import brikkesys_config as config
import pymysql

class Database: # Denne kan være en egen modul. Kall den løperdatabase eller lignende
    def __init__(self, ip_adress):
        self.ip= ip_adress
        self.db = pymysql.connect(**config.get_config(self.ip))
        self.races = []
        self.race_ids = []
        self.cursor = self.db.cursor()
        self.log_file = open("/temp/ospeaker.log", "w")
        try:
            self.read_races()
        except:
            self.log_file.write("No races in database {0}: {1}\n".format(str(self.ip), str(self.ip)))
            self.log_file.flush()
    def update_db(self):
        db = pymysql.connect(**config.get_config(self.num))

    def read_version(self):
        # execute SQL query using execute() method.
        self.cursor.execute("SELECT VERSION()")

        # Fetch a single row using fetchone() method.
        data = self.cursor.fetchone()
        print("Database version : %s " % data)

    # Henter alle løp
    def read_races(self):

        sql = " SELECT * FROM RACES"
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            self.races = self.cursor.fetchall()

        except Exception:
            sql = " SELECT * FROM races"
            self.cursor.execute(sql)
            self.races = self.cursor.fetchall()

        except :
            self.log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
            self.log_file.flush()

    # Henter alle løpernavn
    def read_names(self, race_id):
        self.db.commit()

        try:
            sql = " SELECT * FROM NAMES WHERE RACEID = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            #self.names = self.cursor.fetchall()
            return self.cursor.fetchall()

        except Exception:
            sql = " SELECT * FROM names WHERE raceid = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            # self.names = self.cursor.fetchall()
            return self.cursor.fetchall()

        except:
            self.log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
    def read_names_from_class(self, race_id,class_id):
        self.db.commit()

        try:
            sql = " SELECT * FROM NAMES WHERE RACEID = %(race_id)s AND CLASSID = %(class_id)s"
            self.cursor.execute(sql, {'race_id': race_id, 'class_id': class_id})
            # Fetch all the rows in a list of lists.

            return self.cursor.fetchall()

        except Exception:

            sql = " SELECT * FROM names WHERE raceid = %(race_id)s AND classid = %(class_id)s"
            self.cursor.execute(sql, {'race_id': race_id, 'class_id': class_id})
            # Fetch all the rows in a list of lists.

            return self.cursor.fetchall()

        except:
            self.log_file.write("Unable to fetch names {0}:{1} \n".format(str(sql)), str(class_id))
            self.log_file.flush()
    # Henter alle Klasser
    def read_classes(self,race_id):

        try:
            sql = " SELECT * FROM CLASSES WHERE RACEID = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            self.classes = self.cursor.fetchall()
            # for row in classes:

        except Exception:
            sql = " SELECT * FROM classes WHERE raceid = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            self.classes = self.cursor.fetchall()

        except:
            self.log_file.write("Unable to fetch names {0}:{1} \n".format(str(sql)), str(race_id))
            self.log_file.flush()

    # Henter startnummber fra starnummerdatabasen 
    def read_start_numbers(self):
        self.db.commit()
        sql = " SELECT * FROM startnumbers"
        try:
            # Execute the SQL command
            self.cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            return self.cursor.fetchall()

        except Exception:
            sql = " SELECT * FROM STARTNUMBERS"
            self.cursor.execute(sql)
            return self.cursor.fetchall()

        except:
            self.log_file.write("Unable to fetch data:  {0}: \n".format(str(sql)))
            self.log_file.flush()

