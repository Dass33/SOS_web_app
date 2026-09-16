# Obrázky pro pexeso

Sem patří šestnáct čtvercových fotek, ze kterých se skládá hra na
`/pexeso.html`. Vyrábí je skript z originálů:

    python3 tools/crop-pexeso.py ~/cesta/k/originalum

Skript ořízne každou fotku na čtverec, zmenší ji na 640 × 640 a uloží
jako webp pod těmito názvy:

    hlaska-1, depo33-pred, kaple, obecni-urad, plovarna, poddubi-1,
    depo33-po, rybarska-chata, u-altanu, chaty-za-trati, k-nadrazi,
    hlavni, borovice, houba, tuscany-superb, jezek

Originály sem nepatří, drží se mimo repozitář. U skenu (depo33-pred)
je zdrojem PDF — na to skript potřebuje navíc `pip install pymupdf`.

Stejné názvy (a popisky pro hlasové čtečky) drží seznam `MOTIFS`
v `pexeso.js`. Když nějaký soubor chybí, karta se vykreslí jako barevné
políčko s číslem a hra funguje dál.
