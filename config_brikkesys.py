#!/usr/bin/env python3


def get_config(db):
    ''"Get the appropriate parameters for connecting to the result database"""
    if db == 'local':

        return {

           # local database
               'host':'127.0.0.1',
               'user':'root',
               'passwd':'Purcell18',
              # 'user':'atle',
              # 'passwd':'',
               'db':'resultatdatabase',
               'charset':'utf8'
               }

    elif db == 'Klara':
        # Klaras PC
        return {
              #  'host':'192.168.1.153',
                'host':'169.254.69.147',
                'user':'root',
                'passwd':'Purcell18',
                'db':'resultatdatabase',
                'charset':'utf8'
                }

    elif db ==3:
        # MYSQL
        return {

            'host': '10.218.92.140',
            'user': 'root',
            'passwd': 'Purcell18',
            'db': 'resultatdatabase'
            }


    elif db =='Milo':
        # MYSQL MILO PC
        #    'host': '169.254.136.234',
        return {

            #'host': '169.254.136.234',
            'host': '10.0.0.10',
            'user': 'root',
            'passwd': 'Milo2012',
            'db': 'resultatdatabase'
            }

    elif db =='Prewarn':

        return {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'Purcell18',
            'db': 'startnummerdatabase',
            'charset': 'utf8'
            }


    elif db =='bedrift':
        # MYSQL Bedriftsidretten master
        return {

            'host': '192.168.1.24',
            'user': 'root',
            'passwd': 'ObasWin',
            'db': 'resultatdatabase'
            }
    elif db =='storler':

        return {
                
            'host':'84.214.174.249',
            'user':'root',
            'passwd':'Purcell18',
            'db':'resultatdatabase',
            'charset':'utf8'
            }       

    elif db =='sintefpc8879':

        return {
                
            'host':'169.254.234.122',
            'user':'root',
            'passwd':'Purcell18',
            'db':'resultatdatabase',
            'charset':'utf8'
            }   
        #
#    elif db == 'Startnummerdatabase':
#        return {
#                'host':'127.0.0.1',
#                'user':'root',
#                'password':='Purcell18',
#                'db':'startnummerdatabase',
#                'charset':'utf8',
#                'cursorclass':'pymysql.cursors.DictCursor'
#                }
#


"""

 #self.db = pymysql.connect(host="192.168.1.153",user="root",passwd="Purcell18", db="resultatdatabase", charset='utf8') # Klaras PC
        # local database over Virtual box
        self.db = pymysql.connect(host="192.168.56.1", user="root", passwd="Purcell18", db="resultatdatabase", charset='utf8') # Database over virtualbox
        # db = MySQLdb.connect(host="192.168.1.151", user="root", passwd="Purcell18", db="resultatdatabase", charset='utf8') # Database i PC7486, har ikke turt å skru av brannmuren
        # db = MySQLdb.connect(host="10.218.92.140", user="root", passwd="Purcell18", db="resultatdatabase")
        # db = MySQLdb.connect(host="192.168.1.102", user="root", passwd="Milo2012", db="resultatdatabase")  # For å få kontakt så må vi ha deaktiver brannmur og bruke riktig databbase
       

# Klaras PC MYSQL
        {
            host:'192.168.1.153'
            user:'root'
            passwd:'Purcell18'
            db:'resultatdatabase'
            charset:'utf8'
        }
# Database i PC7486, har ikke turt å skru av brannmuren

        {
            host:'192.168.1.151'
            user:'root'
            passwd:'Purcell18'
            db:'resultatdatabase'
            charset:'utf8'

        }
        

        }
        # MYSQL
        # For å få kontakt så må vi ha deaktiver brannmur og bruke riktig databbase
        {
            host:'192.168.1.102'
            user:'root'
            passwd:'Milo2012'
            db:'resultatdatabase'

        }
        
        
        
        """
