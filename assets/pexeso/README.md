# Obrázky pro pexeso

Sem patří šestnáct čtvercových fotek, ze kterých se skládá hra na
`/pexeso.html`. Vyrábí je skript z originálů:

    python3 tools/crop-pexeso.py ~/cesta/k/originalum

Skript ořízne každou fotku na čtverec, zmenší ji na 640 × 640 a uloží
jako webp pod těmito názvy:

    hlaska-1, hlaska-2, kaple, obecni-urad, plovarna, poddubi-1,
    poddubi-2, rybarska-chata, u-altanu, chaty-za-trati, k-nadrazi,
    hlavni, borovice, houba, tuscany-superb, motiv-16

Stejné názvy (a popisky pro hlasové čtečky) drží seznam `MOTIFS`
v `pexeso.js`. Když nějaký soubor chybí, karta se vykreslí jako barevné
políčko s číslem a hra funguje dál.
