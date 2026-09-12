#!/usr/bin/env python3
"""Ořeže fotky pro pexeso na čtverec a uloží je jako webp do assets/pexeso/.

Použití:
    python3 tools/crop-pexeso.py <slozka-s-originaly> [--size 640]

Potřebuje Pillow:  pip install pillow

Ze vstupní složky se berou soubory podle tabulky MOTIFS níž (hledá se
podle názvu, na velikosti písmen nezáleží). Z každé fotky se vyřízne
největší čtverec a zmenší na --size. Výsledek: assets/pexeso/<slug>.webp
Stejné slugy používá seznam MOTIFS v pexeso.js.
"""

import argparse
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Chybí Pillow. Nainstalujte ho:  pip install pillow")

# (původní soubor, výstupní slug, svislé těžiště ořezu 0.0 = horní okraj,
#  0.5 = střed, 1.0 = spodní okraj)
MOTIFS = [
    ("Hlaska_IMG_20220804_074346.jpg", "hlaska-1", 0.5),
    ("Hlaska_IMG_20220804_074400.jpg", "hlaska-2", 0.5),
    ("Kaple_DSC02315.JPG", "kaple", 0.5),
    ("OU_IMG_20220805_072214.jpg", "obecni-urad", 0.28),
    ("Plovarna_IMG_20220804_075303.jpg", "plovarna", 0.5),
    ("Poddubi_20240622_095722.JPG", "poddubi-1", 0.5),
    ("Poddubi_20240622_095729.JPG", "poddubi-2", 0.5),
    ("Rybarska chata_20240614_183346.JPG", "rybarska-chata", 0.5),
    ("U Altanu_DSC_0040.JPG", "u-altanu", 0.5),
    ("Chaty za trati_20240616_105045.JPG", "chaty-za-trati", 0.5),
    ("K nadrazi_IMG_20210108_140303.jpg", "k-nadrazi", 0.5),
    ("Hlavni_IMG_20210107_130653.jpg", "hlavni", 0.5),
    ("Borovice_DSC_0048.JPG", "borovice", 0.5),
    ("Houba_20251020_160901.JPG", "houba", 0.5),
    ("Tuscany Superb_3.jpg", "tuscany-superb", 0.5),
    ("IMG_0942.jpg", "jezek", 0.5),
]

OUT_DIR = os.path.join("assets", "pexeso")


def find(folder, wanted):
    """Najde soubor bez ohledu na velikost písmen a příponu JPG/jpg."""
    target = wanted.lower()
    base = os.path.splitext(target)[0]
    for name in os.listdir(folder):
        low = name.lower()
        if low == target or os.path.splitext(low)[0] == base:
            return os.path.join(folder, name)
    return None


def square(image, focus):
    """Vyřízne největší čtverec; u výšky se řídí těžištěm focus."""
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = int(round((height - side) * focus))
    top = max(0, min(top, height - side))
    return image.crop((left, top, left + side, top + side))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="složka s originálními fotkami")
    parser.add_argument("--size", type=int, default=640, help="hrana čtverce v px")
    parser.add_argument("--quality", type=int, default=80, help="kvalita webp")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    missing = []

    for filename, slug, focus in MOTIFS:
        path = find(args.source, filename)
        if not path:
            missing.append(filename)
            continue

        with Image.open(path) as image:
            # fotky z mobilu nesou otočení jen v EXIF — bez tohohle by
            # část karet ležela na boku nebo vzhůru nohama
            image = ImageOps.exif_transpose(image).convert("RGB")
            image = square(image, focus)
            image = image.resize((args.size, args.size), Image.LANCZOS)
            out = os.path.join(OUT_DIR, slug + ".webp")
            image.save(out, "WEBP", quality=args.quality, method=6)

        print("%-38s -> %s (%d kB)" % (
            os.path.basename(path), out, os.path.getsize(out) // 1024))

    if missing:
        print("\nNenalezeno ve složce %s:" % args.source, file=sys.stderr)
        for name in missing:
            print("  " + name, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
