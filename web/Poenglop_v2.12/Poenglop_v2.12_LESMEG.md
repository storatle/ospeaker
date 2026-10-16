# Poengløp v2.12 – poengberegning for lommelyktløp i Brikkesys

Tidligere navn: Poeng. Full bruksanvisning finnes i appen under **Bruksanvisning**.

## Mappestruktur
    C:\Poenglop\Poenglop_v2.12
    C:\Poenglop\Poenglop_BrikkesysAPI_v1.4

Ikke bruk C:\Program Files. Start med `Start_Poenglop.bat`. Uten Brikkesys: `Start_Poenglop_testmodus.bat`.
På Ubuntu/Linux: `./start_poenglop.sh` og `./start_poenglop_testmodus.sh`. Se `Poenglop_v2.12_INSTALLASJON_UBUNTU.txt`.
Filnavnene skrives «Poenglop» uten ø, fordi Windows-kommandovinduet kan feile på æ, ø og å i filnavn. I appen heter løsningen Poengløp.

## Oppgradering fra Poengløp v2.11
1. Pakk ut `Poenglop_v2.12` ved siden av `Poenglop_BrikkesysAPI_v1.4` (API-et er uendret).
2. Kopier `poeng-data`, `poeng-config.json` og egne oppsettfiler (*.json) fra `Poenglop_v2.11`.
3. Lukk v2.11 og start `Start_Poenglop.bat`. Poengløp leser nå MySQL direkte med tilkoblingen fra API-mappen. Ingen nytt oppsett trengs.

Fra v2.10 eller eldre: følg punktene over, og trykk «Finn tabeller automatisk» og «Bruk forslaget» hvis meldingen «Oppsettet av tabeller passer ikke» kommer.

## Nytt i v2.12
- **Direkte lesing fra MySQL**: Poengløp kan lese Brikkesys-databasen selv, uten at Brikkesys-API må kjøre. Velges under **Oppsett → Tilkobling til Brikkesys → Lesemåte**:
  - **Automatisk** (standard): direkte når MySQL-driveren og brukernavnet finnes, ellers via Brikkesys-API.
  - **Direkte fra MySQL**: bare direkte.
  - **Gjennom Brikkesys-API**: som før.
- Står brukernavnet tomt, brukes tilkoblingen fra `poeng-brikkesys-config.json` i API-mappen, så en eksisterende installasjon virker uten nytt oppsett. Server, port, database, brukernavn, passord og tegnsett kan også legges inn under Oppsett, f.eks. for å lese fra løps-PC-en over nettverket.
- MySQL-driveren (`mysql2`) hentes fra API-mappen, eller installeres av `Start_Poenglop.bat` første gang (krever internett).
- I Automatisk går Poengløp over til direkte lesing av seg selv når MySQL kommer opp, også om API-et ble brukt ved oppstart.
- **Sikkerhet**: Poengløp kjører bare SELECT. Tabell- og kolonnenavn fra oppsettet kontrolleres mot databasen før de brukes. Passordet sendes aldri til nettleseren, men lagres i klartekst i `poeng-config.json` – del aldri den filen.
- Brikkesys-API trengs fortsatt for full eksport til filer og databaseoversikten på http://127.0.0.1:8091.
- **Ubuntu/Linux**: startskript (`start_poenglop.sh`, `start_poenglop_testmodus.sh`, og .sh-versjoner av API-skriptene) og egen installasjonsbeskrivelse. Skriptene kontrollerer Node.js-versjonen og åpner nettleseren.
- `npm test` starter testmodus (pekte på en fil som ikke fantes).
- Bruksanvisningen er oppdatert.

## Nytt i v2.11 (tidligere versjon)
- **Standardkobling mot Brikkesys**: Løp = `races`, Deltakere = `names`, Stemplinger = `controltimes` (`controlcode`), Klasser med målpost = `classes` (`codes`). En ny installasjon virker uten oppsett hvis kolonnenavnene stemmer. Ellers retter «Finn tabeller automatisk» dem.
- **Poster pr løype er fjernet**. Postene, målposten og løypen hentes fra `classes`. Postene i `codes` (unntatt siste) brukes til å vise hvilke poster deltakeren ikke har tatt.
- **Løype fra classes**: har ikke deltakeren løype i `names`, brukes løypen til klassen i `classes`.
- **Målpost-oppsettet under Poengkategorier er fjernet**. Målposten er alltid siste verdi i `classes.codes`. Uten målpost i `classes` får ikke løperen godkjent tid.
- **Oppsett → Målpost** viser målpost pr klasse og kontrollen mot stemplingene (kun visning).
- Utgåtte innstillinger (målpost skrevet inn for hånd, målpostkolonne for løp, poster pr løype) ignoreres i eldre oppsett.

**Ikke verifisert mot ekte Brikkesys:** kolonnenavnene utenom `controltimes.controlcode` og `classes.codes`, f.eks. `names.raceid`, `names.class`, `classes.class` og `classes.course`.

## Nytt i v2.10
- **Målpost pr klasse fra Brikkesys**: målposten er siste verdi i `codes` i tabellen `classes`. Poengløp henter den automatisk for hver klasse, så klasser kan ha ulik målpost (f.eks. 100 og 150).
- Ny gruppe under Oppsett → Tabeller og kolonner: «Klasser med postkoder – målpost er siste verdi» (tabell, løps-ID, klasse-ID, klassenavn, postkoder). Gjenkjenningen finner den automatisk.
- Kontrollen mot stemplingene gjøres nå pr klasse. Avvik vises med «ventet …».
- Rekkefølge: kode skrevet inn i Poengløp → `classes.codes` pr klasse → målpostkolonne for løpet → kontrollert siste stempling i `controltimes`.
- Testløpene har målpost 150 for familieklassene og 100 for de andre.
- Bruksanvisningen er oppdatert.

## Nytt i v2.9 (kodegjennomgang: sikkerhet og ytelse)
**Sikkerhet**
- Andre nettsider som åpnes på samme PC kan ikke lenger lese deltakerdata eller endre oppsettet. Før svarte begge serverne med `Access-Control-Allow-Origin: *`.
- Vern mot DNS-rebinding: bare forespørsler til 127.0.0.1/localhost på riktig port godtas.
- Skrivende kall krever egen header (vern mot CSRF).
- Sikkerhetshoder: Content-Security-Policy, X-Frame-Options, nosniff, Referrer-Policy.
- CSV-eksport kan ikke lenger inneholde Excel-formler fra navn eller klubb (f.eks. «=HYPERLINK(…)»).
- Ingen eksterne ressurser: Google Fonts er fjernet. Appen virker helt uten internett og sender ingen data ut.
- Advarsel hvis serverne konfigureres til å lytte på annet enn 127.0.0.1.
- Brikkesys-API v1.4 har de samme rettingene.

**Ytelse**
- Tabellene i Deltakere og Resultatliste tegnes bare når fanen vises. Et tastetrykk med 600 deltakere tar ca. 40 ms (før ca. 460 ms).
- Mengdene for ignorerte koder og målpost lages én gang pr beregning.

**Kvalitet**
- ESLint uten funn. Ingen kjente sårbarheter i avhengigheter (npm audit).

## Nytt i v2.8
- **Målpost fra stemplingene, med kontroll**: målposten er normalt siste `controlcode` i tabellen `controltimes`. Poengløp finner den automatisk, men tar den bare i bruk når kontrollen er bestått:
  - samme kode er siste stempling for minst 90 % av deltakerne i mål
  - stempletiden på koden stemmer med målgangen (±3 sek) for minst 90 %
- Resultatet av kontrollen vises under Målpost, med ✓/✗ og navn på deltakere som avviker.
- Feiler kontrollen, brukes ikke koden. «Bruk likevel» eller en kode skrevet inn for hånd tar den i bruk.
- En kode fra innstillingen eller fra løpstabellen i Brikkesys går foran og blir også kontrollert mot stemplingene.
- Standardoppsett for stemplinger (gjelder nye installasjoner): tabell `controltimes`, kolonne `controlcode`. Gjenkjenningen foretrekker nå `controltimes`.
- Testløpene finner målposten 100 via stemplingene (normaltilfellet).

**Ikke verifisert:** at `controltimes`/`controlcode` er strukturen i alle Brikkesys-versjoner. Det finnes ingen offentlig dokumentasjon. Kontrollen i appen fanger opp avvik i dine egne data.

## Nytt i v2.7
- Tabellen «Siste i mål» er forenklet: Deltaker, Klasse, Løype, I mål, Løpstid, Poeng (totalt), Tidsjustering, Totaltid og – helt til høyre – plassen i løypen eller klassen.
- Kolonnene pr poengkategori er fjernet fra denne tabellen. De vises fortsatt i resultatlisten under.
- Den nyeste i mål har merket «Sist i mål».
- Bruksanvisningen er oppdatert.

## Nytt i v2.6
- **Målpost** (Poengkategorier → Grunninnstillinger): koden på målposten, f.eks. 100, 150 eller 170.
  - Normalt hentes den fra Brikkesys: Oppsett → Tabeller og kolonner → Løp → «Målpostkode» (ny, valgfri). Automatisk gjenkjenning foreslår kolonnen hvis den finnes.
  - Skrives en kode inn under Grunninnstillinger, overstyrer den Brikkesys. Flere koder kan skilles med komma.
  - Er målposten ukjent, foreslår Poengløp koden som nesten alle i mål har som siste stempling, med en knapp for å ta den i bruk.
  - Viser hvor mange i mål som har stempling på målposten, og advarer hvis ingen har det.
- Stempletiden på målposten brukes som tid for Mål i postrekker og strekk. Uten stempling brukes løpstiden som før.
- Målposten gir aldri postpoeng og vises ikke i postlisten. Den trenger ikke lenger stå under «Postkoder som ikke gir poeng».
- Testløpene har målpost 100 i «Brikkesys», med stempling ved målgang.
- Bruksanvisningen er oppdatert.

## Nytt i v2.5
- **Start (0)** og **Mål** kan velges som poster i poengkategoriene Postrekke, Strekk innen tid og Raskeste på strekk:
  - strekket fra start til første post, f.eks. Raskeste fra Start til 31
  - strekket fra siste post inn til mål, f.eks. 50 → Mål på høyst 30 sek
  - postrekker som begynner med start, f.eks. Start → 31 → 32
- Start har tid 0 og Mål har løpstiden, når stempletidene i Brikkesys er regnet fra start (vanligst). Poengløp ser dette selv pr deltaker.
- Er stempletidene klokkeslett, brukes den nye valgfrie kolonnen **Starttid** (Oppsett → Tabeller og kolonner → Deltakere). Mangler den, viser poengkategorien en advarsel.
- Start og mål vises med o-kartets symboler: trekant og dobbel ring.
- Nye testløpere: Test Startsprint og Test Målspurt. TEST_poengoppsett.json har tre nye poengkategorier som bruker Start og Mål.
- Bruksanvisning og fasit er oppdatert.

## Nytt i v2.4
- «Siste i mål» viser **Plass nå**, for eksempel «3. av 12», i deltakerens løype eller klasse (etter valgt visning og sortering).
- Plassen regnes ut på nytt ved hver oppdatering.
- Endring siden målgang vises med pil: «↓2» når deltakeren er passert av noen som kom senere, «↑1» når hen har rykket opp. Hold musen over pilen for å se plassen ved målgang.
- Bruksanvisningen er oppdatert.

## Nytt i v2.3
- **Siste i mål** øverst i resultatlisten: de 5 siste som er registrert i mål, på tvers av alle løyper og klasser, med den nyeste øverst.
- Tabellen har samme kolonner som resultatlisten, i tillegg til klokkeslett i mål, løype eller klasse (etter valgt visning) og plass der.
- Den nyeste raden er farget. Nye rader blinker kort ved oppdatering.
- Slås av med «Vis 5 siste i mål». Tabellen kommer ikke med på utskriften.
- Rekkefølgen følger samme regel som «Sist i mål»: kolonnen «Registrert tidspunkt» hvis den er satt opp, ellers tidspunktet Poengløp så deltakeren få tid (krever automatisk oppdatering).
- Bruksanvisningen er oppdatert.

## Nytt i v2.2
- Resultatlisten sorteres som standard på **lavest totaltid**. Ved lik totaltid kommer den med flest poeng først. «Flest poeng, så lavest tid» kan fortsatt velges.
- CSV-eksporten følger valgt sortering.
- Utskrift: hver løype eller klasse starter på ny side. Løpets navn og tidspunktet for siste lesing står øverst på hver side, og kolonneoverskriftene gjentas når en løype eller klasse går over flere sider.
- Bruksanvisningen er oppdatert.

## Nytt i v2.1
- Testløpene vises nå som standard, i en egen gruppe «Testløp – finnes bare i Poengløp» nederst i nedtrekksmenyen. Ekte løp ligger under «Løp i Brikkesys».
- Før var testløpene skjult som standard, så de så ut til å mangle etter en ny installasjon.
- Innstillinger kopiert fra tidligere versjoner skjuler dem ikke lenger.
- Testløpene kan fortsatt skjules under Oppsett → Testdata.
- Bruksanvisningen er oppdatert.

## Oppgradering fra Poeng v1.8
1. Pakk ut begge mappene til `C:\Poenglop`.
2. Kopier `poeng-brikkesys-config.json` fra den gamle API-mappen til `Poenglop_BrikkesysAPI_v1.4`. Kjør `0_Test_tilkobling.bat` der én gang.
3. Kopier `poeng-data`, `poeng-config.json` og egne parameterfiler (*.json) fra `Poeng_v1.8` til `Poenglop_v2.12`.
4. Lukk Poeng v1.8 og start `Start_Poenglop.bat`.

Lagrede parametere fra tidligere versjoner virker uendret. De får automatisk riktig poengkategori.
Filnavnene `poeng-data`, `poeng-config.json` og `poeng-brikkesys-config.json` er beholdt, slik at de kan kopieres rett over.

## Nytt i v2.0 (tidligere versjon)
- Nytt navn: **Poengløp** (før: Poeng).
- «Parametere» heter nå **Poengkategorier**.
- Fanen Poengkategorier er delt i tre trinn: Grunninnstillinger, Postpoeng og Ekstra poengkategorier.
- Sju egne knapper for poengkategorier, hver med forklaring og eksempel:
  Klasse, løype eller alder · Løpstid · Postrekke · Strekk innen tid · Raskeste på strekk · Manuell tildeling · Kombinerte vilkår.
- Hver kategori viser bare feltene den trenger.
- **Bonus** eller **Straff** velges med knapp i stedet for pluss- og minustall.
- Regelen vises i klartekst, for eksempel «Deltakere med løpstid høyst 40 min får 8 straffepoeng (1:20 lengre tid)».
- «Gjelder nå» viser hvilke deltakere kategorien treffer.
- Kategori kan byttes. Valg som ikke hører til den nye kategorien, fjernes.
- Parameterfil heter nå **Poengoppsett i fil**. Testfilen heter `TEST_poengoppsett.json`. Filer fra tidligere versjoner kan hentes.
- Brikkesys-API heter nå **Poengløp Brikkesys-API v1.3**. Kun navneendring.
- Bruksanvisningen er skrevet om med de nye navnene og en oversikt over kategoriene.

## Tidligere versjoner (Poeng)
- v1.8: «Sist i mål» pr løype/klasse.
- v1.7: testløp med fasit og live-testløp.
- v1.6: Postrekke.
- v1.5: automatisk oppdatering.
- v1.4: parameterkort og parameterfil.
- v1.3: automatisk tabellgjenkjenning, resultatdatabase.
- v1.2: Strekk – raskeste tid.
- v1.1: data via Brikkesys-API.
- v1.0: første versjon.
