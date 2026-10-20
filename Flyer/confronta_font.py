#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera un flyer COMPLETO per ciascun font script installato, per confrontare
lo stile del titolo "Il potere della musica" nel contesto reale.

Output: Flyer/output/Confronto_Font/<NomeFont>.png  (formato social leggero)

Uso:  ../.venv/bin/python confronta_font.py
"""

import os
import genera_flyer as gf

FONTS = {
    "Kaushan-Script": "Kaushan-Script.ttf",
    "Dancing-Script": "DancingScript[wght].ttf",
    "Pacifico": "Pacifico-Regular.ttf",
    "Sacramento": "Sacramento-Regular.ttf",
    "Parisienne": "Parisienne-Regular.ttf",
    "Allura": "Allura-Regular.ttf",
    "Yellowtail": "Yellowtail-Regular.ttf",
    "Satisfy": "Satisfy-Regular.ttf",
}

FONT_DIR = os.path.expanduser("~/.local/share/fonts/")


def main():
    outdir = os.path.join(gf.OUTPUT_DIR, "Confronto_Font")
    os.makedirs(outdir, exist_ok=True)
    flyer = gf.FLYERS[0]
    size = (1080, 1620)  # formato social leggero per confronto rapido

    for label, fname in FONTS.items():
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            print(f"[SALTO] Font mancante: {label} ({fname})")
            continue
        # imposta il font script globale usato da compose()
        gf.FONT_SCRIPT = path
        img = gf.compose(flyer, size)
        out = os.path.join(outdir, f"{label}.png")
        img.save(out, "PNG")
        print(f"[OK] {label:16s} ->  {out}")

    print("\nConfronto pronto in ./output/Confronto_Font/")


if __name__ == "__main__":
    main()
