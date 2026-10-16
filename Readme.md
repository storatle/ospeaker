BrikkeSpy er et python3 program som leser inn løp fra Brikkesys databasen på en LøpsPC. 
Ved hjelp av BrikkeSpy så kan du få frem resultater og se hvilke løpere som er i mål og hvilke løpere som fortsatt er ute i skogen. 
I tilegg har man mulighet til å lese inn forvarsel fra en annen pc. For å få til dette så må man ha en local myscl database på PCen


Dette må du gjøre på LøpsPC med Brikkesys:

Åpne innstillinger skriv Firewall og velg "Brannmur og nettverksbeskyttelse"
Skru av brannmuren på "Offentlig nettverk"
Åpne kommandovindu og skriv ipconfig. Då får du nettverksadressen.


Dette må du gjøre på PC med BrikkeSpy:(linux maskin)
Gå inn på Wired Connected og velg Wired settings.
Klikk på tannhjulet og klikk på IPv4 og så velger du "Link-Local Only".

Åpne en terminal og skriv ifconfig
sjekk om du har fått en ip-adresse

skriv ping Løperpc-adresse.

start brikkespy med følgende kommndo

python brikkespy.py Milo (kommando for løpspc) 

Slik oppdaterer du mysqldatabasene
mysql -u root -p resultatdatabase < 20201017T190939_17.sql (Hentet fra brikkesys) 

Windows
For det første bør du installere *cmder* for å få et fornuftig kommandoshell i windows. 
Da kan du hente inn _Branch: windows_ og 
Så må du installerer Python3 og Pillow 


Disse modulene kreves for å kjøre Brikkespy:
tkinter - installer med: sudo apt-get install python3-tk
pymysql - pip3 install pymysql
PyPDF2 - sudo pip3 install PyPDF2, hvis intallasjonen feiler prøv: pip3 install --upgrade setuptools
reportlab - sudo pip3 install reportlab
PIL - pip3 install pillow
screeninfo - pip install screeninfo

Hvis du skal bruke din egen prewarn system så må du sette opp en prewarndatabase på en annen pc.
Dette må testes på nytt for nå er brikkespy endret 
Dette må du gjøre på BrikkeSpy-PC for at PC med prewarn skal ha tilgang til databasen
mysql -u root -p
mysql> CREATE USER 'root'@'ip_adresse_prewarnpc' IDENTIFIED WITH mysql_native_password BY 'Password';
mysql> GRANT ALL ON startnummerdatabase.* TO 'root'@'ip_adresse_prewarnpc';
mysql> FLUSH PRIVILEGES;

MySQL lytter som standard bare på 127.0.0.1. For at prewarn-PC skal komme til, må bind-address i
/etc/mysql/mysql.conf.d/mysqld.cnf settes til 0.0.0.0 (eller PC-ens IP), og så: sudo systemctl restart mysql

-----------------------------------------------------------------------------------------------
Dette må du gjøre hvis du har en helt ny mysql database:
NB! du skal ikke sette noe annet passord enn mysql_native_passord

NB! du kan også gjøre dette når pymysql ikke kan lese databsesn; Når du får følgende feilmelding: pymysql.err.OperationalError: (1698, "Access denied for user 'root'@'localhost'")

På Ubuntu bruker root auth_socket som standard, og da ignoreres passordet. Slik setter du passordinnlogging (MySQL 8):

sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '<passord>'; FLUSH PRIVILEGES;"

Passordet må være det samme som i config_database.py (eller i miljøvariabelen DB_PASSWORD_LOCAL).
Test at det virker:

mysql -u root -p -h 127.0.0.1 -e "SHOW DATABASES;"

NB! Etter dette virker ikke "sudo mysql" uten passord lenger, bruk "mysql -u root -p".

Lage ny database
mysql> show databases;
mysql> DROP DATABASE database;  
mysql> CREATE DATABASE database;  
mysql> Exit;

mysql -u root -p resultatdatabase < 20201017T190939_17.sql (Hentet fra brikkesys) 
