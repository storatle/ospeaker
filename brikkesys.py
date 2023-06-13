#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import config_database as config
import pymysql
import sys
from datetime import datetime

class Database: # Denne kan være en egen modul. Kall den løperdatabase eller lignende
    def __init__(self, ip_adress):
        self.db = pymysql.connect(**config.get_config(ip_adress))
        self.races = []
        self.race_ids = []
        self.cursor = self.db.cursor()
        if sys.platform == "win32":
            self.log_file = open("ospeaker.log", "w")
        else:
            self.log_file = open("/var/log/ospeaker.log", "w")
        try:
            self.read_races()
        except:
            self.log_file.write("No races in database {0}: {1}\n".format(str(ip_adress), str(ip_adress)))
            self.log_file.flush()

    def update_db(self):
        db = pymysql.connect(**config.get_config(self.num))

    def read_version(self):
        # execute SQL query using execute() method.
        self.cursor.execute("SELECT VERSION()")

        # Fetch a single row using fetchone() method.
        data = self.cursor.fetchone()
        #print("Database version : %s " % data)

    def read_online(self, race_id):
        #print("Brikkesys.py read_online race_id={}".format(race_id))
        self.db.commit()
        #print("{} - db.read_online(self, race_id) ".format(datetime.now().strftime("%H:%M:%S")))
        sql = " SELECT * FROM ONLINECONTROLS WHERE RACEID = %(race_id)s"
        try:
            # Execute the SQL command
            self.cursor.execute(sql, {'race_id': race_id})
            # Fetch all the rows in a list of lists.
            return self.cursor.fetchall()
        except Exception:
            sql = " SELECT * FROM onlinecontrols WHERE raceid = %(race_id)s"
            self.cursor.execute(sql, {'race_id': race_id})
            return self.cursor.fetchall()
        except :
            self.log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
            self.log_file.flush()
    
    def read_eventor_personid(self, person_id):
        #print(person_id)
        sql = " SELECT * FROM eventor_personid WHERE bid = %(person_id)s"
        try: 
            self.cursor.execute(sql, {'person_id': person_id})
            return self.cursor.fetchall()

        except :
            self.log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
            self.log_file.flush()

    def read_eventor_club(self, club_id):

        sql = " SELECT * FROM eventor_clubs WHERE organisationid = %(club_id)s"
        try:
            self.cursor.execute(sql, {'club_id': club_id})
            return self.cursor.fetchall()
 
        except :
            self.log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
            self.log_file.flush()


    def read_invoicelevel(self, race_id):
        sql = " SELECT * FROM invoicelevels WHERE raceid = %(id)s"
        try:
            self.cursor.execute(sql, {'id': race_id})
            return self.cursor.fetchall()
 
        except :
            self.log_file.write("Unable to fetch data {0}: \n".format(str(sql)))
            self.log_file.flush()


    # Henter alle løp
    def read_races(self):

        sql = " SELECT * FROM RACES"
        #print("{} - db.read_races(self)".format(datetime.now().strftime("%H:%M:%S")))
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
        
        #print("{0} - db.read_names(self, race_id={1})".format(datetime.now().strftime("%H:%M:%S"),race_id))

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

    def read_names_from_class(self, race_id, class_id):
        self.db.commit()
        #print("{0} - db.read_names_from_classes(self, race_id={1}, class_id={2})".format(datetime.now().strftime("%H:%M:%S"),race_id,class_id))

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

        #print("{} - db.read_classes(self, race_id)".format(datetime.now().strftime("%H:%M:%S")))
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

    # Henter startnummber fra starnummerdatabasen, denne leser ikke fra brikkesys 
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

