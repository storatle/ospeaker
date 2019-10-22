BrikkeSpy er et python3 program som leser inn løp fra Brikkesys databasen på en LøpsPC. 
Ved hjelp av BrikkeSpy kan du få frem resultater og se hvilke løpere som er i mål og hvilke løpere som fortsatt er ute i skogen. 
I tilegg har man mulighet til å lese inn forvarsel fra en annen pc. For å få til dette så må man ha en local myscl database på PCen
Brikkespy har også resultatservice som gir deg mulighet til å vise resultatene live på storskjerm. Enten kan man vise klassevis eller så kan man lage en loop.


Dette må du gjøre på LøpsPC med Brikkesys for å få kommunikasjon med den:

Åpne innstillinger skriv Firewall og velg "Brannmur og nettverksbeskyttelse"
Skru av brannmuren på "Offentlig nettverk"
Åpne kommandovindu og skriv ipconfig. Da får du nettverksadressen.


Dette må du gjøre på PC med BrikkeSpy:
Gå inn på Wired Connected og velg Wired settings.
Klikk på tannhjulet og klikk på IPv4 og så velger du "Link-Local Only".

Åpne en terminal og skriv ifconfig
sjekk om du har fått en ip-adresse

skriv ping Løperpc-adresse.

Dette må du gjøre på BrikkeSpy-PC for at PC med prewarn skal ha tilgang til databasen
mysql -u root -p
GRANT ALL ON startnummerdatabase.* TO root@ip_adresse_prewarnpc  IDENTIFIED BY 'Password';
FLUSH PRIVILEGES;*


Windows

For det første bør du installere *cmder* for å få et fornuftig kommandoshell i windows. 
Da kan du hente inn _Branch: windows_ og 
Så må du installerer Python3 og Pillow 


Disse modulene kreves for å kjøre Brikkespy:
tkinter - installer med: sudo apt-get install python3-tk
pymysql - pip3 install pymysql

PyPDF2 - sudo pip3 install PyPDF2, hvis intallasjonen feiler prøv: pip3 install --upgrade setuptools
PIL - pip3 install pillow
reportlab -  pip3 install reportlab 

Todo-list for versjon 2.0
Merge Poengo inn i orace.py
Sjekk om startlister fungerer tilfredstillende.
Fiks liste ved målgang som viser siste innkomende løper, med klass og foreløpig plassering. Liste som ruller nedover.


