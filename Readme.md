Dette må du gjøre på Løperpc:

Åpne innstillinger skriv Firewall og vedl "Brannmur og nettverksbeskyttelse"
Skru av brannmuren på "Offentlig nettverk"
Åpne kommandovindu og skriv ipconfig. Då får du nettverksadressen.


Dette må du gjøre på Perseus:
Gå inn på Wired Connected og velg Wired settings.
Klikk på tannhjulet og klikk på IPv4 og så velger du "Link-Local Only".

Åpne en terminal og skriv ifconfig
sjekk om du har fått en ip-adresse

skriv ping Løperpc-adresse.

Dette må du gjøre på Perseus for at PC med prewarn skal ha tilgang til databasen
mysql -u root -p
GRANT ALL ON startnummerdatabase.* TO root@ip_adresse_prewarnpc  IDENTIFIED BY 'Password';
FLUSH PRIVILEGES;*


Windows

For det første bør du installere *cmder* for å få et fornuftig kommandoshell i windows. 

Da kan du hente inn _Branch: windows_ og 

Så må du installerer Python3 og Pillow 

