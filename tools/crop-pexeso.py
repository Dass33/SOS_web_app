#!/usr/bin/env python3
"""Ořeže fotky pro pexeso na čtverec a uloží je jako webp do assets/pexeso/.

Použití:
    python3 tools/crop-pexeso.py <slozka-s-originaly> [--size 640]

Potřebuje Pillow:  pip install pillow

Ze vstupní složky se berou soubory podle tabulky MOTIFS níž (hledá se
podle názvu, na velikosti písmen nezáleží). Z každé fotky se vyřízne
největší čtverec a zmenší na --size. Výsledek: assets/pexeso/<slug>.webp
Stejné slugy používá seznam MOTIFS v pexeso.js.

Zdrojem může být i PDF se skenem (pak je potřeba i PyMuPDF:
pip install pymupdf) — vytáhne se z něj fotka a ořeže bílý okraj skenu.
"""

import argparse
import io
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Chybí Pillow. Nainstalujte ho:  pip install pillow")

# (původní soubor, výstupní slug, svislé těžiště ořezu 0.0 = horní okraj,
#  0.5 = střed, 1.0 = spodní okraj). Čtvrtý prvek je volitelné vodorovné
#  těžiště (0.0 = levý okraj, 0.5 = střed, 1.0 = pravý) — bez něj se řeže
#  na střed.
MOTIFS = [
    ("Hlaska_IMG_20220804_074346.jpg", "hlaska-1", 0.5),
    ("img303.pdf", "depo33-pred", 0.5, 0.47),
    ("Kaple_DSC02315.JPG", "kaple", 0.5),
    ("OU_IMG_20220805_072214.jpg", "obecni-urad", 0.28),
    ("Plovarna_IMG_20220804_075303.jpg", "plovarna", 0.5),
    ("Poddubi_20240622_095722.JPG", "poddubi-1", 0.5),
    ("IMG_9354.JPG", "depo33-po", 0.5, 0.28),
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


def square(image, focus, focus_x=0.5):
    """Vyřízne největší čtverec podle zadaných těžišť."""
    width, height = image.size
    side = min(width, height)
    left = int(round((width - side) * focus_x))
    left = max(0, min(left, width - side))
    top = int(round((height - side) * focus))
    top = max(0, min(top, height - side))
    return image.crop((left, top, left + side, top + side))


def open_source(path):
    """Načte fotku; z PDF vytáhne sken a odřízne jeho bílý okraj."""
    if not path.lower().endswith(".pdf"):
        return Image.open(path)

    try:
        import pymupdf
    except ImportError:
        sys.exit("Na PDF je potřeba PyMuPDF:  pip install pymupdf")

    page = pymupdf.open(path)[0]
    images = page.get_images(full=True)
    if not images:
        sys.exit("V PDF %s není žádná fotka." % path)

    data = page.parent.extract_image(images[0][0])
    scan = Image.open(io.BytesIO(data["image"])).convert("RGB")
    return trim_border(scan)


def trim_border(image, threshold=225, inset=16):
    """Odřízne bílý okraj skenu a ještě kousek navíc, ať nesvítí zbytek.

    Jednotlivé smítka v okraji by bounding box roztáhla, proto se řeže
    podle řádků a sloupců: okraj je ten, kde skoro nic není.
    """
    ink = image.convert("L").point(lambda v: 0 if v > threshold else 255)
    width, height = ink.size
    rows = list(ink.resize((1, height), Image.BOX).getdata())
    cols = list(ink.resize((width, 1), Image.BOX).getdata())

    def span(values, limit=38):
        start = 0
        while start < len(values) and values[start] < limit:
            start += 1
        end = len(values) - 1
        while end > start and values[end] < limit:
            end -= 1
        return start, end + 1

    top, bottom = span(rows)
    left, right = span(cols)
    left, top = left + inset, top + inset
    right, bottom = right - inset, bottom - inset
    if right - left < 1 or bottom - top < 1:
        return image
    return image.crop((left, top, right, bottom))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="složka s originálními fotkami")
    parser.add_argument("--size", type=int, default=640, help="hrana čtverce v px")
    parser.add_argument("--quality", type=int, default=80, help="kvalita webp")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    missing = []

    for motif in MOTIFS:
        filename, slug, focus = motif[:3]
        focus_x = motif[3] if len(motif) > 3 else 0.5
        path = find(args.source, filename)
        if not path:
            missing.append(filename)
            continue

        with open_source(path) as image:
            # fotky z mobilu nesou otočení jen v EXIF — bez tohohle by
            # část karet ležela na boku nebo vzhůru nohama
            image = ImageOps.exif_transpose(image).convert("RGB")
            image = square(image, focus, focus_x)
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
