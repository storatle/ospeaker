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
GRANT ALL ON startnummerdatabase.* TO root@ip_adresse_prewarnpc  IDENTIFIED BY 'Password';
FLUSH PRIVILEGES;*

-----------------------------------------------------------------------------------------------
Dette må du gjøre hvis du har en helt ny mysql database:
NB! du skal ikke sette noe annet passord enn mysql_native_passord
sudo mysql -u root # I had to use "sudo" since it was a new installation

mysql> USE mysql;
mysql> UPDATE user SET plugin='mysql_native_password' WHERE User='root';
mysql> FLUSH PRIVILEGES;
mysql> exit;

sudo service mysql restart

Lage ny database
mysql> DROP DATABASE database;  
mysql> CREATE DATABASE database;  
mysql> Exit;

mysql -u root -p resultatdatabase < 20201017T190939_17.sql (Hentet fra brikkesys) 
