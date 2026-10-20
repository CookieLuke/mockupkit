#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore di immagini promozionali (mockup) per Google Play Store
Brand: "Special Forces Training" - tema tattico/militare.

Output: 8 immagini 1080x1920 verticali nella cartella ./output/

Requisiti:
    - Python 3
    - Pillow  (pip install Pillow)
    - Font Oswald (variable font) installato nel sistema

Uso:
    python3 genera_immagini.py
"""

import os
import math
import random
import argparse
import sys
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ----------------------------------------------------------------------------
# CONFIGURAZIONE
# ----------------------------------------------------------------------------

CANVAS_W, CANVAS_H = 1080, 1920

# Palette tattica
COL_BG_TOP     = (26, 26, 26)      # #1A1A1A antracite
COL_BG_BOTTOM  = (10, 12, 10)      # quasi nero con leggero verde oliva
COL_OLIVE      = (34, 40, 28)      # verde oliva molto scuro (pattern)
COL_WHITE      = (245, 245, 245)
COL_RED        = (211, 47, 47)     # #D32F2F rosso sangue
COL_ORANGE     = (255, 87, 34)     # #FF5722 arancione tattico
COL_PHONE_BODY = (18, 18, 18)      # corpo telefono
COL_PHONE_EDGE = (70, 74, 68)      # bordo metallico

# Percorso font Oswald (variable font). Fallback su ricerca fc-match.
OSWALD_PATH = "/home/luca/.local/share/fonts/Oswald-VariableFont_wght.ttf"

# Logo del brand (PNG con trasparenza, senza riquadro blu)
LOGO_PATH = "icone_altro/IconMock.png"

# Frazione dello screenshot da tagliare in basso per rimuovere la barra di
# navigazione di sistema Android (il minimo indispensabile).
BOTTOM_CROP_FRACTION = 0.038

OUTPUT_DIR = "output"

# ----------------------------------------------------------------------------
# PRESET DEI DISPOSITIVI
# ----------------------------------------------------------------------------
# Ogni preset definisce: dimensioni canvas, cartella di output, tipo di
# cornice ("phone" o "tablet") e alcuni parametri di scala per testo/logo.
# I testi e gli screenshot restano identici per tutti i preset.
DEVICE_PRESETS = [
    {
        "name": "Smartphone",
        "canvas": (1080, 1920),
        "outdir": os.path.join(OUTPUT_DIR, "Assets Smartphone"),
        "frame": "phone",
        "scale": 1.0,
    },
    {
        "name": "Tablet 7",
        "canvas": (1200, 1920),
        "outdir": os.path.join(OUTPUT_DIR, "Assets Tablet 7"),
        "frame": "tablet",
        "scale": 1.05,
    },
    {
        "name": "Tablet 10",
        "canvas": (1200, 1920),
        "outdir": os.path.join(OUTPUT_DIR, "Assets Tablet 10"),
        "frame": "tablet",
        "scale": 1.05,
    },
]

# Preset attualmente attivo (impostato a runtime da main()). Le funzioni di
# disegno leggono CANVAS_W/CANVAS_H e CURRENT_FRAME/CURRENT_SCALE globali.
CURRENT_FRAME = "phone"
CURRENT_SCALE = 1.0

# Storyboard: (nome_file_screenshot, titolo, parola_chiave_da_evidenziare, sottotitolo)
# La parola chiave viene cercata (case-insensitive) nel titolo e colorata.
STORYBOARD = [
    ("UNO_Screenshot_016Home1.png",
     "ADDESTRATI COME L'ÉLITE",
     "ÉLITE",
     "Preparati a spingerti oltre."),

    ("DUE_Screenshot_003SistemaProgressione.png",
     "UN SISTEMA COMPLETO DI PROGRESSIONE",
     "PROGRESSIONE",
     "Da neofita a operatore avanzato, tutto sotto controllo."),

    ("TRE_Screenshot_007LeForzeSpeciali.png",
     "LE FORZE SPECIALI ITALIANE",
     "SPECIALI",
     "Descrizione, caratteristiche e test di selezione."),

    ("QUATTRO_Screenshot_008Allenamento1Sett.png",
     "8 SETTIMANE PER LIVELLO FINO ALL'OBIETTIVO",
     "OBIETTIVO",
     "Piani strutturati giorno per giorno."),

    ("CINQUE_Screenshot_009CrossFit.png",
     "PROGRAMMA CROSSFIT",
     "CROSSFIT",
     "Istruzioni precise per massimizzare la resa."),

    ("SEI_Screenshot_012Progressi.png",
     "TRACCIA I TUOI PROGRESSI",
     "PROGRESSI",
     "Monitora le tue prestazioni sul campo con streak motivazionali."),

    ("SETTE_Screenshot_013Salute.png",
     "PRIVACY ASSOLUTA",
     "PRIVACY",
     "Monitora le tue metriche. I dati restano solo sul tuo dispositivo."),

    ("OTTO_Screenshot_014Community.png",
     "SCALA LA CLASSIFICA",
     "CLASSIFICA",
     "Confrontati con la community e domina la leaderboard globale."),
]

# Colore accento per ciascuna immagine (alterniamo rosso/arancio per varietà controllata)
ACCENTS = [COL_RED, COL_ORANGE, COL_RED, COL_ORANGE,
           COL_RED, COL_ORANGE, COL_RED, COL_ORANGE]


# ----------------------------------------------------------------------------
# FONT HELPERS
# ----------------------------------------------------------------------------

def load_font(size, weight="Bold"):
    """Carica Oswald al peso richiesto. Il file e' variabile: proviamo a
    impostare l'asse 'wght'. Fallback: font di default."""
    try:
        f = ImageFont.truetype(OSWALD_PATH, size)
        try:
            axes = {"Light": 300, "Regular": 400, "Medium": 500,
                    "SemiBold": 600, "Bold": 700}
            f.set_variation_by_axes([axes.get(weight, 700)])
        except Exception:
            pass
        return f
    except Exception:
        return ImageFont.load_default()


# ----------------------------------------------------------------------------
# BACKGROUND
# ----------------------------------------------------------------------------

def make_gradient(w, h, top, bottom):
    """Gradiente verticale."""
    base = Image.new("RGB", (w, h), top)
    top_r, top_g, top_b = top
    bot_r, bot_g, bot_b = bottom
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top_r + (bot_r - top_r) * t)
        g = int(top_g + (bot_g - top_g) * t)
        b = int(top_b + (bot_b - top_b) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return base


def add_camo_pattern(img, seed=0):
    """Aggiunge un pattern mimetico quasi invisibile (blob organici scuri)."""
    random.seed(seed)
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n_blobs = 26
    for _ in range(n_blobs):
        cx = random.randint(-100, w + 100)
        cy = random.randint(-100, h + 100)
        rad = random.randint(120, 340)
        # blob come poligono irregolare
        pts = []
        steps = random.randint(7, 11)
        for i in range(steps):
            ang = (2 * math.pi / steps) * i
            rr = rad * random.uniform(0.6, 1.15)
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        shade = random.choice([COL_OLIVE, (22, 22, 22), (30, 32, 26)])
        alpha = random.randint(18, 34)  # molto sottile
        d.polygon(pts, fill=(shade[0], shade[1], shade[2], alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    return img.convert("RGB")


def add_grunge(img, seed=0):
    """Texture grunge marcata: rumore metallico + graffi/venature + macchie."""
    random.seed(seed + 999)
    w, h = img.size

    # 1) Rumore fine (grana metallica) - piu' visibile
    noise = Image.new("L", (w, h))
    npx = noise.load()
    for y in range(h):
        for x in range(w):
            npx[x, y] = random.randint(0, 255)
    noise = noise.filter(ImageFilter.GaussianBlur(0.5))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, noise_rgb, alpha=0.11)

    # 2) Venature/graffi metallici sottili (linee diagonali chiaro/scuro)
    scratch = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scratch)
    for _ in range(38):
        x0 = random.randint(-50, w)
        y0 = random.randint(-50, h)
        length = random.randint(120, 520)
        ang = random.uniform(-0.5, 0.5) + random.choice([0.0, math.pi / 2])
        x1 = x0 + length * math.cos(ang)
        y1 = y0 + length * math.sin(ang)
        light = random.random() < 0.5
        col = (255, 255, 255, random.randint(6, 16)) if light \
            else (0, 0, 0, random.randint(10, 24))
        sd.line([(x0, y0), (x1, y1)], fill=col, width=random.choice([1, 1, 2]))
    scratch = scratch.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.alpha_composite(img.convert("RGBA"), scratch).convert("RGB")

    # 3) Macchie grunge irregolari (sporco/usura) sparse
    stains = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    st = ImageDraw.Draw(stains)
    for _ in range(60):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        r = random.randint(30, 160)
        a = random.randint(6, 20)
        tone = random.choice([(0, 0, 0), (255, 255, 255), COL_OLIVE])
        st.ellipse([cx - r, cy - r, cx + r, cy + r],
                   fill=(tone[0], tone[1], tone[2], a))
    stains = stains.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img.convert("RGBA"), stains).convert("RGB")

    return img


def add_vignette(img):
    """Vignettatura scura ai bordi per dare profondita'."""
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w * 0.25, -h * 0.15, w * 1.25, h * 1.15], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(img, dark, mask)


def build_background(seed):
    bg = make_gradient(CANVAS_W, CANVAS_H, COL_BG_TOP, COL_BG_BOTTOM)
    bg = add_camo_pattern(bg, seed)
    bg = add_grunge(bg, seed)
    bg = add_vignette(bg)
    return bg


# ----------------------------------------------------------------------------
# PHONE MOCKUP
# ----------------------------------------------------------------------------

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)
    return m


def build_phone(screenshot_path, target_h):
    """Crea l'immagine RGBA di uno smartphone con lo screenshot dentro.
    target_h = altezza desiderata del corpo del telefono in pixel."""
    shot = Image.open(screenshot_path).convert("RGB")
    # Taglia il minimo indispensabile in basso per rimuovere la barra di
    # navigazione di sistema Android, per un look piu' pulito.
    if BOTTOM_CROP_FRACTION > 0:
        sw0, sh0 = shot.size
        crop_px = int(sh0 * BOTTOM_CROP_FRACTION)
        shot = shot.crop((0, 0, sw0, sh0 - crop_px))
    sw, sh = shot.size
    aspect = sw / sh

    # Dimensioni schermo in base all'altezza target
    bezel = max(10, int(target_h * 0.011))     # cornice sottile
    body_border = bezel                          # spessore telaio
    screen_h = target_h - 2 * body_border
    screen_w = int(screen_h * aspect)

    body_w = screen_w + 2 * body_border
    body_h = target_h

    screen_radius = int(screen_w * 0.075)
    body_radius = screen_radius + body_border

    # --- corpo telefono ---
    phone = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(phone)
    # telaio esterno (bordo metallico)
    pd.rounded_rectangle([0, 0, body_w, body_h], radius=body_radius,
                         fill=COL_PHONE_EDGE)
    # corpo interno nero
    inset = max(2, int(body_border * 0.35))
    pd.rounded_rectangle([inset, inset, body_w - inset, body_h - inset],
                         radius=body_radius - inset, fill=COL_PHONE_BODY)

    # --- schermo (screenshot con angoli arrotondati) ---
    screen = shot.resize((screen_w, screen_h), Image.LANCZOS)
    smask = rounded_mask((screen_w, screen_h), screen_radius)
    phone.paste(screen, (body_border, body_border), smask)

    # --- punch-hole camera (in alto al centro) ---
    hole_r = max(7, int(screen_w * 0.016))
    hx = body_border + screen_w // 2
    hy = body_border + int(screen_h * 0.022)
    pd.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r],
               fill=(5, 5, 5))
    pd.ellipse([hx - hole_r + 2, hy - hole_r + 2, hx + hole_r - 2, hy + hole_r - 2],
               outline=(40, 40, 45), width=1)

    # --- riflesso/gloss diagonale sottile sullo schermo ---
    gloss = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.polygon([(body_border, body_border),
                (body_border + int(screen_w * 0.5), body_border),
                (body_border, body_border + int(screen_h * 0.45))],
               fill=(255, 255, 255, 16))
    gloss.putalpha(gloss.split()[3].filter(ImageFilter.GaussianBlur(6)))
    # applichiamo il gloss solo dentro lo schermo
    gloss_masked = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    full_screen_mask = Image.new("L", (body_w, body_h), 0)
    ImageDraw.Draw(full_screen_mask).rounded_rectangle(
        [body_border, body_border, body_border + screen_w, body_border + screen_h],
        radius=screen_radius, fill=255)
    gloss_masked.paste(gloss, (0, 0), full_screen_mask)
    phone = Image.alpha_composite(phone, gloss_masked)

    return phone


def build_tablet(screenshot_path, target_h):
    """Crea l'immagine RGBA di un TABLET con lo screenshot dentro.
    Rispetto allo smartphone: telaio piu' spesso e uniforme, angoli meno
    arrotondati, camera centrata sul bordo superiore. Lo screenshot (verticale
    stretto) viene inserito nello schermo del tablet, con fasce laterali scure
    eleganti ai lati per riempire il diverso aspect ratio."""
    shot = Image.open(screenshot_path).convert("RGB")
    if BOTTOM_CROP_FRACTION > 0:
        sw0, sh0 = shot.size
        crop_px = int(sh0 * BOTTOM_CROP_FRACTION)
        shot = shot.crop((0, 0, sw0, sh0 - crop_px))
    sw, sh = shot.size
    shot_aspect = sw / sh

    # Aspect ratio dello SCHERMO del tablet (portrait 10:16 ~ 0.625, look 16:10)
    screen_aspect = 0.66  # leggermente piu' largo dello smartphone

    # telaio tablet: piu' spesso e uniforme
    body_border = max(24, int(target_h * 0.028))
    screen_h = target_h - 2 * body_border
    screen_w = int(screen_h * screen_aspect)

    body_w = screen_w + 2 * body_border
    body_h = target_h

    # angoli meno arrotondati rispetto allo smartphone
    screen_radius = int(screen_w * 0.03)
    body_radius = int(screen_radius + body_border * 0.7)

    # --- corpo tablet ---
    tablet = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    td = ImageDraw.Draw(tablet)
    # telaio esterno (metallo)
    td.rounded_rectangle([0, 0, body_w, body_h], radius=body_radius,
                         fill=COL_PHONE_EDGE)
    # corpo interno scuro
    inset = max(3, int(body_border * 0.28))
    td.rounded_rectangle([inset, inset, body_w - inset, body_h - inset],
                         radius=max(2, body_radius - inset), fill=COL_PHONE_BODY)

    # --- contenuto dello schermo: screenshot centrato con fasce laterali ---
    # Riempiamo l'area schermo con uno sfondo scuro coerente col tema, poi
    # incolliamo lo screenshot centrato mantenendo il suo aspect ratio.
    screen_bg = Image.new("RGB", (screen_w, screen_h), (16, 16, 16))
    # scala lo screenshot per adattarlo in ALTEZZA allo schermo del tablet
    ss_h = screen_h
    ss_w = int(ss_h * shot_aspect)
    if ss_w > screen_w:
        # se troppo largo, adatta in larghezza
        ss_w = screen_w
        ss_h = int(ss_w / shot_aspect)
    shot_resized = shot.resize((ss_w, ss_h), Image.LANCZOS)
    ox = (screen_w - ss_w) // 2
    oy = (screen_h - ss_h) // 2

    # fasce laterali: sfumatura scura verticale per un look elegante
    if ox > 0:
        band = make_gradient(screen_w, screen_h, (28, 30, 26), (12, 14, 12))
        screen_bg.paste(band, (0, 0))
    screen_bg.paste(shot_resized, (ox, oy))

    # sottile bordo separatore tra screenshot e fasce laterali
    if ox > 0:
        sb = ImageDraw.Draw(screen_bg)
        sb.line([(ox, 0), (ox, screen_h)], fill=(60, 64, 58), width=2)
        sb.line([(ox + ss_w, 0), (ox + ss_w, screen_h)], fill=(60, 64, 58), width=2)

    # applica angoli arrotondati allo schermo
    smask = rounded_mask((screen_w, screen_h), screen_radius)
    tablet.paste(screen_bg, (body_border, body_border), smask)

    # --- camera centrata sul bordo superiore (piccola) ---
    hole_r = max(5, int(body_border * 0.16))
    hx = body_w // 2
    hy = body_border // 2
    td.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r],
               fill=(5, 5, 5))
    td.ellipse([hx - hole_r + 1, hy - hole_r + 1, hx + hole_r - 1, hy + hole_r - 1],
               outline=(45, 48, 52), width=1)

    # --- gloss diagonale sottile sullo schermo ---
    gloss = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.polygon([(body_border, body_border),
                (body_border + int(screen_w * 0.55), body_border),
                (body_border, body_border + int(screen_h * 0.4))],
               fill=(255, 255, 255, 14))
    gloss.putalpha(gloss.split()[3].filter(ImageFilter.GaussianBlur(8)))
    full_screen_mask = Image.new("L", (body_w, body_h), 0)
    ImageDraw.Draw(full_screen_mask).rounded_rectangle(
        [body_border, body_border, body_border + screen_w, body_border + screen_h],
        radius=screen_radius, fill=255)
    gloss_masked = Image.new("RGBA", (body_w, body_h), (0, 0, 0, 0))
    gloss_masked.paste(gloss, (0, 0), full_screen_mask)
    tablet = Image.alpha_composite(tablet, gloss_masked)

    return tablet


def add_shadow(canvas, obj_rgba, pos):
    """Incolla obj_rgba su canvas in pos, con ombra morbida sotto."""
    ox, oy = pos
    w, h = obj_rgba.size
    # ombra
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    alpha = obj_rgba.split()[3]
    sh_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    black = Image.new("RGBA", (w, h), (0, 0, 0, 150))
    sh_layer.paste(black, (0, 0), alpha)
    shadow.paste(sh_layer, (ox + 12, oy + 26), sh_layer)
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(obj_rgba, (ox, oy), obj_rgba)
    return canvas


# ----------------------------------------------------------------------------
# TESTO
# ----------------------------------------------------------------------------

def wrap_text(draw, text, font, max_w):
    """Manda a capo il testo per rientrare in max_w."""
    words = text.split()
    lines = []
    cur = ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_title(draw, lines, font, keyword, accent, top_y, max_w, line_gap):
    """Disegna il titolo centrato, evidenziando la keyword con accent."""
    kw = keyword.upper()
    y = top_y
    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    for line in lines:
        # calcolo larghezza totale della riga per centrare
        total_w = draw.textlength(line, font=font)
        x = (CANVAS_W - total_w) / 2
        # disegniamo parola per parola per colorare la keyword
        words = line.split(" ")
        cx = x
        for i, wd in enumerate(words):
            piece = wd + (" " if i < len(words) - 1 else "")
            color = accent if wd.strip(",.'").upper() == kw else COL_WHITE
            # ombra testo
            draw.text((cx + 3, y + 3), piece, font=font, fill=(0, 0, 0))
            draw.text((cx, y), piece, font=font, fill=color)
            cx += draw.textlength(piece, font=font)
        y += line_h + line_gap
    return y


def draw_subtitle(draw, text, font, y, max_w, accent):
    lines = wrap_text(draw, text, font, max_w)
    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    for line in lines:
        total_w = draw.textlength(line, font=font)
        x = (CANVAS_W - total_w) / 2
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(210, 210, 210))
        y += line_h + 6
    return y


def draw_accent_bar(draw, y, accent, width=140, thickness=8):
    x0 = (CANVAS_W - width) / 2
    draw.rounded_rectangle([x0, y, x0 + width, y + thickness],
                           radius=thickness // 2, fill=accent)


# ----------------------------------------------------------------------------
# LOGO / BRAND MARK
# ----------------------------------------------------------------------------

def draw_logo(canvas, accent):
    """Inserisce il logo SFT (ovale/basco, sfondo trasparente) in alto a
    sinistra con marchio testuale accanto. Il testo sta su una riga se
    entra nello spazio, altrimenti va su due righe."""
    margin = 55
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
    except Exception:
        return canvas

    logo_h = 110
    ratio = logo.width / logo.height
    logo = logo.resize((int(logo_h * ratio), logo_h), Image.LANCZOS)

    # ombra morbida basata sulla sagoma (alpha) del logo
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    black = Image.new("RGBA", logo.size, (0, 0, 0, 120))
    sh.paste(black, (0, 0), logo.split()[3])
    shadow.paste(sh, (margin + 4, margin + 5), sh)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(logo, (margin, margin), logo)

    # marchio testuale accanto al logo
    tx = margin + logo.width + 24
    d = ImageDraw.Draw(canvas)
    brand_font = load_font(40, "Bold")

    available_w = CANVAS_W - tx - margin
    one_line_w = d.textlength("SPECIAL FORCES TRAINING", font=brand_font)
    asc, desc = brand_font.getmetrics()
    line_h = asc + desc

    if one_line_w <= available_w:
        # UNA RIGA: "SPECIAL FORCES " bianco + "TRAINING" accento,
        # centrato verticalmente rispetto al logo.
        ty = margin + (logo_h - line_h) // 2
        part1 = "SPECIAL FORCES "
        w1 = d.textlength(part1, font=brand_font)
        d.text((tx + 2, ty + 2), part1, font=brand_font, fill=(0, 0, 0))
        d.text((tx, ty), part1, font=brand_font, fill=COL_WHITE)
        d.text((tx + w1 + 2, ty + 2), "TRAINING", font=brand_font, fill=(0, 0, 0))
        d.text((tx + w1, ty), "TRAINING", font=brand_font, fill=accent)
    else:
        # DUE RIGHE, centrate verticalmente rispetto al logo.
        block_h = line_h * 2 - desc
        ty = margin + (logo_h - block_h) // 2
        d.text((tx + 2, ty + 2), "SPECIAL FORCES", font=brand_font, fill=(0, 0, 0))
        d.text((tx, ty), "SPECIAL FORCES", font=brand_font, fill=COL_WHITE)
        line2_y = ty + line_h - 4
        d.text((tx + 2, line2_y + 2), "TRAINING", font=brand_font, fill=(0, 0, 0))
        d.text((tx, line2_y), "TRAINING", font=brand_font, fill=accent)
    return canvas


# ----------------------------------------------------------------------------
# COMPOSIZIONE DI UNA SINGOLA IMMAGINE
# ----------------------------------------------------------------------------

def compose(index, screenshot, title, keyword, subtitle, accent):
    canvas = build_background(seed=index).convert("RGBA")

    # logo/brand in alto a sinistra
    canvas = draw_logo(canvas, accent)

    draw = ImageDraw.Draw(canvas)

    # --- AREA TESTO (alto ~25%) ---
    margin_x = 70
    max_text_w = CANVAS_W - 2 * margin_x

    # dimensione titolo adattiva
    title_size = 96
    title_font = load_font(title_size, "Bold")
    lines = wrap_text(draw, title, title_font, max_text_w)
    # riduci se troppe righe
    while len(lines) > 3 and title_size > 60:
        title_size -= 6
        title_font = load_font(title_size, "Bold")
        lines = wrap_text(draw, title, title_font, max_text_w)

    # abbassiamo il titolo per lasciare spazio al logo/brand in alto
    top_y = 210
    y_after_title = draw_title(draw, lines, title_font, keyword, accent,
                               top_y, max_text_w, line_gap=4)

    # barra accento
    draw_accent_bar(draw, y_after_title + 10, accent)

    # sottotitolo
    sub_font = load_font(38, "Regular")
    y_after_sub = draw_subtitle(draw, subtitle, sub_font,
                                y_after_title + 34, max_text_w, accent)

    # --- DEVICE (occupa lo spazio in basso) ---
    device_top = int(y_after_sub + 40)
    available_h = CANVAS_H - device_top - 30
    if CURRENT_FRAME == "tablet":
        device = build_tablet(screenshot, target_h=available_h)
    else:
        device = build_phone(screenshot, target_h=available_h)

    # se troppo largo, riscala per larghezza
    max_device_w = CANVAS_W - 120
    if device.width > max_device_w:
        scale = max_device_w / device.width
        device = device.resize((int(device.width * scale),
                                int(device.height * scale)), Image.LANCZOS)

    px = (CANVAS_W - device.width) // 2
    py = device_top + max(0, (available_h - device.height) // 2)
    canvas = add_shadow(canvas, device, (px, py))

    return canvas.convert("RGB")


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

def _load_config(path):
    """Carica un file YAML e restituisce la configurazione come dizionario."""
    if not HAS_YAML:
        print("ERRORE: PyYAML non installato. Esegui:  pip install pyyaml")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _storyboard_from_config(cfg):
    """Converte la sezione 'slides' del config YAML nello stesso formato
    del STORYBOARD interno: lista di tuple (screenshot, titolo, keyword, sub)."""
    result = []
    for s in cfg.get("slides", []):
        result.append((
            s["screenshot"],
            s["titolo"],
            s.get("keyword", s["titolo"].split()[0]),
            s.get("sottotitolo", ""),
        ))
    return result


def _devices_from_config(cfg):
    """Converte la sezione 'devices' del config YAML nel formato DEVICE_PRESETS."""
    result = []
    for d in cfg.get("devices", []):
        result.append({
            "name": d.get("name", "Device"),
            "canvas": tuple(d["canvas"]),
            "outdir": d["outdir"],
            "frame": d.get("frame", "phone"),
            "scale": float(d.get("scale", 1.0)),
        })
    return result


def main():
    global CANVAS_W, CANVAS_H, CURRENT_FRAME, CURRENT_SCALE, LOGO_PATH

    # ------------------------------------------------------------------ CLI
    parser = argparse.ArgumentParser(
        description="Genera mockup promozionali per il Play Store.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python genera_immagini.py                       # usa il codice interno (ITA)
  python genera_immagini.py --config config/ITA.yaml
  python genera_immagini.py --config config/ENG.yaml
  python genera_immagini.py --config config/ENG.yaml --device smartphone
        """,
    )
    parser.add_argument(
        "--config", "-c",
        metavar="FILE.yaml",
        help="Percorso al file di configurazione YAML (vedi config/ITA.yaml).",
    )
    parser.add_argument(
        "--device", "-d",
        metavar="NOME",
        help='Genera solo il preset con questo nome (es. "Smartphone", "Tablet 7").'
             " Usa 'all' per tutti (default).",
        default="all",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Mostra i dispositivi definiti nel config e termina.",
    )
    args = parser.parse_args()

    # ---------------------------------------------------------- carica config
    if args.config:
        cfg = _load_config(args.config)
        storyboard = _storyboard_from_config(cfg)
        presets    = _devices_from_config(cfg)
        # logo opzionale da config
        logo_in_cfg = cfg.get("logo", "").strip()
        if logo_in_cfg:
            LOGO_PATH = logo_in_cfg
    else:
        storyboard = [(s, t, k, sub) for s, t, k, sub in STORYBOARD]
        presets    = DEVICE_PRESETS

    # ------------------------------------------------------ --list-devices
    if args.list_devices:
        print("Dispositivi disponibili:")
        for p in presets:
            print(f"  • {p['name']}  {p['canvas']}  frame={p['frame']}")
        return

    # -------------------------------------------- filtra per --device
    if args.device.lower() != "all":
        presets = [p for p in presets
                   if p["name"].lower() == args.device.lower()]
        if not presets:
            print(f"ERRORE: nessun preset con nome '{args.device}'.")
            print("Usa --list-devices per vedere quelli disponibili.")
            sys.exit(1)

    # ----------------------------------------------------- generazione
    nums = [f"{i+1:02d}" for i in range(len(storyboard))]

    for preset in presets:
        CANVAS_W, CANVAS_H = preset["canvas"]
        CURRENT_FRAME       = preset["frame"]
        CURRENT_SCALE       = preset["scale"]
        outdir              = preset["outdir"]
        os.makedirs(outdir, exist_ok=True)

        print(f"\n=== {preset['name']}  ({CANVAS_W}x{CANVAS_H}, "
              f"cornice: {CURRENT_FRAME}) ===")
        for i, (shot, title, kw, sub) in enumerate(storyboard):
            if not os.path.exists(shot):
                print(f"[SALTO] Screenshot mancante: {shot}")
                continue
            accent = ACCENTS[i % len(ACCENTS)]
            img = compose(i, shot, title, kw, sub, accent)
            out = os.path.join(outdir, f"PlayStore_{nums[i]}.png")
            img.save(out, "PNG")
            print(f"[OK] {out}  <-  {shot}")

    print(f"\nFatto! Asset generati nelle cartelle configurate.")


if __name__ == "__main__":
    main()
