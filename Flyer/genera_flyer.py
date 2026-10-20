#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore di FLYER / LOCANDINE - Biodanza (stile acquerello elegante)

Partendo da un'immagine di sfondo (illustrazione acquerello con ampi spazi
in alto e in basso), sovrappone i testi in modo elegante e coerente:
  - logo in alto a sinistra (opzionale)
  - etichetta occhiello (es. "Stage di Biodanza")
  - titolo principale in corsivo script (Dancing Script)
  - sottotitolo e riga descrittiva (serif elegante)
  - badge circolare con una nota
  - fascia in basso con data / orario / luogo / contatti

Genera DUE versioni per ogni flyer:
  - STAMPA: alta risoluzione (A4 300 DPI, 2480x3508) -> sottocartella "Stampa"
  - SOCIAL: versione leggera (1080x1620) -> sottocartella "Social"

Requisiti: Python 3, Pillow, font Dancing Script + un serif/sans di sistema.

Uso:  ../.venv/bin/python genera_flyer.py
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ----------------------------------------------------------------------------
# PERCORSI
# ----------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Immagine di sfondo pulita (illustrazione, spazi liberi sopra/sotto)
BACKGROUND_PATH = os.path.join(BASE_DIR, "biodanza_flyer_candidate_b_thirds(2).png")

# Logo (PNG trasparente). Se non esiste, verra' usato un placeholder testuale.
LOGO_PATH = os.path.join(ASSETS_DIR, "Logo_Biodanza_Toro.png")

# Se True, rimuove lo sfondo uniforme del logo rendendolo trasparente.
# Il logo Logo_Biodanza_Toro.png ha gia' sfondo crema coerente col flyer,
# quindi non serve alcuna rimozione (evita sbavature sui contorni).
LOGO_REMOVE_BG = False

# ----------------------------------------------------------------------------
# FONT
# ----------------------------------------------------------------------------

FONT_SCRIPT = os.path.expanduser("~/.local/share/fonts/Parisienne-Regular.ttf")
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# ----------------------------------------------------------------------------
# PALETTE (tonalita' calde/acquerello, coerenti con lo sfondo)
# ----------------------------------------------------------------------------

COL_TITLE = (178, 88, 58)       # terracotta caldo (come il titolo esempio)
COL_DARK = (74, 68, 62)         # grigio-bruno per testi principali
COL_SOFT = (120, 112, 104)      # grigio-caldo per testi secondari
COL_BADGE_LINE = (178, 88, 58)  # bordo badge terracotta
COL_WHITE = (250, 248, 244)

# ----------------------------------------------------------------------------
# CONFIGURAZIONE DEI FLYER (config-driven: aggiungi elementi alla lista)
# ----------------------------------------------------------------------------
# Ogni flyer e' un dizionario. I campi vuoti/None vengono semplicemente saltati.
FLYERS = [
    {
        "id": "potere_della_musica",
        "background": BACKGROUND_PATH,
        "occhiello": "Stage di Biodanza",
        "titolo": "Il potere\ndella musica",
        "sottotitolo": "Come e perché la musica ci nutre",
        "descrizione": "Un viaggio teorico ed esperienziale sul potere musicale",
        "badge": "Musiche coinvolgenti e movimenti naturali per un benessere psico-corporeo profondo. Gioia, armonia, rilassamento. ",
        # --- fascia inferiore: COLONNA SINISTRA (info evento, ~2/3) ---
        # 'info_evento' e' una lista di RIGHE. Ogni riga e' un dict:
        #   "text": stringa (puo' contenere marcatori inline)
        #   "style": stile base della riga -> "title" (grande terracotta bold),
        #            "bold" (nero grassetto), "reg" (normale), "soft" (tenue)
        #   "space_after": spazio extra sotto la riga (frazione di H), opzionale
        # Marcatori inline per evidenziare parole:
        #   [[parola]]  -> colore terracotta/corallo (accento)
        #   {{parola}}  -> grassetto
        "info_evento": [
            {"text": "DOMENICA 15 NOVEMBRE", "style": "title"},
            {"text": "Ore 10.00 - 13.00", "style": "subtitle",
             "space_after": 0.010},
            {"text": "Presso: Laboratorio Olistico Samsara", "style": "bold"},
            {"text": "Via Pacinotti 24/bis - [[TORINO]]", "style": "reg"},
            {"text": "Zona S. Donato, vicino a Piazza Statuto",
             "style": "soft", "space_after": 0.010},
            {"text": "Le [[Iscrizioni]] sono aperte, con quota ridotta entro il 31 ottobre.",
             "style": "reg"},
            {"text": "I posti sono limitati per garantire la cura del gruppo.", "style": "reg"},
            {"text": "Per info e iscrizioni scrivi su WhatsApp al "
                     "{{328 8558169}}", "style": "reg",
             "space_after": 0.008},
            {"text": "Primo stage mensile su {{I poteri"
                     " della Biodanza}}, la partecipazione agli altri 3 stage è consigliata, ma non vincolante.", "style": "soft"},
        
        ],
        # --- fascia inferiore: COLONNA DESTRA (conduttrice, ~1/3) ---
        "conduttrice": {
            "foto": os.path.join(ASSETS_DIR, "SoniaTrinchero.jpg"),
            "nome": "Conduce: Dott.ssa Sonia Trinchero",
            "ruolo": "Operatrice, Tutor e Didatta di Biodanza SRTA",
            "note": "{{www.danziamolavita.com}}",
        },
    },
]

# ----------------------------------------------------------------------------
# PRESET DI OUTPUT (stampa + social)
# ----------------------------------------------------------------------------
# Il layout e' definito in coordinate RELATIVE (0..1) rispetto alla dimensione
# del canvas, cosi' lo stesso disegno scala perfettamente su qualsiasi formato.
OUTPUT_PRESETS = [
    {"name": "Stampa", "size": (2480, 3508), "dpi": 300, "subdir": "Stampa"},
    {"name": "Social", "size": (1080, 1620), "dpi": 72, "subdir": "Social"},
    # Instagram quadrato: il flyer verticale viene centrato su canvas 1:1
    # con sfondo crema esteso ai lati (nessun contenuto tagliato).
    {"name": "Instagram", "size": (1080, 1620), "dpi": 72,
     "subdir": "Instagram", "square": 1080},
]

# Colore di riempimento per il letterbox Instagram (crema, come lo sfondo).
COL_CREAM = (250, 247, 241)


# ----------------------------------------------------------------------------
# FONT HELPERS
# ----------------------------------------------------------------------------

def _load(path, size, fallback=None):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype(fallback, size) if fallback else \
                ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()


def font_script(size):
    f = _load(FONT_SCRIPT, size, FONT_SERIF_ITALIC)
    # Dancing Script e' variabile: prova ad impostare un peso pieno
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    return f


def font_serif(size, italic=False):
    return _load(FONT_SERIF_ITALIC if italic else FONT_SERIF, size)


def font_sans(size, bold=False):
    return _load(FONT_SANS_BOLD if bold else FONT_SANS, size)


# ----------------------------------------------------------------------------
# TEXT UTILS
# ----------------------------------------------------------------------------

def wrap(draw, text, font, max_w):
    """Manda a capo rispettando eventuali newline espliciti (\n)."""
    out_lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            out_lines.append("")
            continue
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if draw.textlength(test, font=font) <= max_w or not cur:
                cur = test
            else:
                out_lines.append(cur)
                cur = w
        out_lines.append(cur)
    return out_lines


def line_height(font, factor=1.12):
    asc, desc = font.getmetrics()
    return int((asc + desc) * factor)


def fit_one_line(draw, text, make_font, size_start, size_min, max_w):
    """Riduce la dimensione finche' il testo entra in UNA riga in max_w.
    make_font(size) -> font. Ritorna (font, lines) dove lines e' 1 elemento
    se ci sta, altrimenti fa il wrap come fallback."""
    size = size_start
    f = make_font(size)
    while size > size_min and draw.textlength(text, font=f) > max_w:
        size -= 1
        f = make_font(size)
    if draw.textlength(text, font=f) <= max_w:
        return f, [text]
    return f, wrap(draw, text, f, max_w)


def draw_multiline(draw, lines, font, cx, y, fill, align="center",
                   left_x=None, line_factor=1.12, shadow=None):
    """Disegna piu' righe. align: center|left. Ritorna la y finale."""
    lh = line_height(font, line_factor)
    for line in lines:
        w = draw.textlength(line, font=font)
        if align == "center":
            x = cx - w / 2
        else:
            x = left_x if left_x is not None else cx
        if shadow:
            sx, sy, scol = shadow
            draw.text((x + sx, y + sy), line, font=font, fill=scol)
        draw.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


# ----------------------------------------------------------------------------
# ELEMENTI GRAFICI
# ----------------------------------------------------------------------------

def _logo_transparent(logo, tol=40):
    """Rende trasparente lo sfondo uniforme del logo (rileva il colore
    dell'angolo in alto a sinistra e azzera l'alpha dei pixel simili)."""
    logo = logo.convert("RGBA")
    px = logo.load()
    w, h = logo.size
    bg = px[0, 0][:3]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if abs(r - bg[0]) <= tol and abs(g - bg[1]) <= tol and \
                    abs(b - bg[2]) <= tol:
                px[x, y] = (r, g, b, 0)
    return logo


def paste_logo(canvas, W, H):
    """Logo in alto a sinistra. Se manca il file, scrive un placeholder."""
    margin = int(W * 0.05)
    draw = ImageDraw.Draw(canvas)
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        if LOGO_REMOVE_BG:
            logo = _logo_transparent(logo)
        target_w = int(W * 0.22)
        ratio = logo.height / logo.width
        logo = logo.resize((target_w, int(target_w * ratio)), Image.LANCZOS)
        canvas.paste(logo, (margin, margin), logo)
    else:
        f = font_sans(int(W * 0.022), bold=True)
        draw_multiline(draw, ["BIODANZA", "ROLANDO", "TORO"], f,
                       0, margin, COL_DARK, align="left",
                       left_x=margin, line_factor=1.02)


def draw_badge(canvas, text, W, H):
    """Badge circolare (occhiello con nota) in alto a sinistra, sotto il logo."""
    if not text:
        return
    draw = ImageDraw.Draw(canvas)
    cx = int(W * 0.15)
    cy = int(H * 0.20)          # piu' in basso per non toccare il logo
    # Dimensioni del badge: metà larghezza e metà altezza
    rx = int(W * 0.12)
    ry = int(H * 0.085)
    # cerchio con bordo terracotta sottile
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                 outline=COL_BADGE_LINE, width=max(2, int(W * 0.0018)))
    # testo interno
    f = font_sans(int(W * 0.021))
    max_w = int(rx * 1.5)
    lines = wrap(draw, text, f, max_w)
    lh = line_height(f, 1.12)
    total_h = lh * len(lines)
    y = cy - total_h / 2
    draw_multiline(draw, lines, f, cx, y, COL_DARK, align="center",
                   line_factor=1.12)


def oval_photo(photo, size, border=False):
    """Ritaglia una foto in forma OVALE (ellisse), senza bordo per default.
    La foto viene adattata con COVER + crop centrale (niente deformazioni):
    riempie l'ovale mantenendo le proporzioni originali del viso.
    Ritorna un'immagine RGBA delle dimensioni 'size' (w,h)."""
    w, h = size
    src = photo.convert("RGB")
    sw, sh = src.size
    # scala 'cover': riempi (w,h) mantenendo aspect, poi ritaglia al centro
    scale = max(w / sw, h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    resized = src.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    ph = resized.crop((left, top, left + w, top + h))
    # maschera ellittica con anti-alias (render 4x poi downscale)
    ss = 4
    mask = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, w * ss, h * ss], fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(ph, (0, 0), mask)
    if border:
        ImageDraw.Draw(out).ellipse([0, 0, w - 1, h - 1],
                                    outline=COL_BADGE_LINE,
                                    width=max(2, int(w * 0.02)))
    return out


def parse_rich(text):
    """Trasforma una stringa con marcatori inline in una lista di token:
      [[..]] -> accento (terracotta)   {{..}} -> bold
    Ritorna lista di (parola, flag_accento, flag_bold), gia' divisa per parole
    cosi' da poter fare il wrapping."""
    import re
    tokens = []
    # dividiamo la stringa in segmenti marcati e non
    pattern = re.compile(r"(\[\[.*?\]\]|\{\{.*?\}\})")
    for seg in pattern.split(text):
        if not seg:
            continue
        accent = bold = False
        content = seg
        if seg.startswith("[[") and seg.endswith("]]"):
            accent = True
            content = seg[2:-2]
        elif seg.startswith("{{") and seg.endswith("}}"):
            bold = True
            content = seg[2:-2]
        # dividiamo in parole mantenendo gli spazi come separatori
        words = content.split(" ")
        for i, w in enumerate(words):
            if w == "" and i not in (0, len(words) - 1):
                continue
            tokens.append([w, accent, bold])
    return tokens


def _tok_font(base_font_reg, base_font_bold, bold):
    return base_font_bold if bold else base_font_reg


def draw_rich_line(draw, tokens, x, y, max_w, f_reg, f_bold,
                   col_reg, col_accent, line_factor=1.35):
    """Disegna una riga 'rich' (token con accento/bold) allineata a sinistra,
    con word-wrap entro max_w. Ritorna la y finale."""
    space_w_reg = draw.textlength(" ", font=f_reg)
    lh = line_height(f_bold, line_factor)
    cx = x
    first_in_line = True
    for word, accent, bold in tokens:
        # le parole con accento (terracotta) vengono rese anche in BOLD
        # per massima visibilita'.
        f = _tok_font(f_reg, f_bold, bold or accent)
        col = col_accent if accent else col_reg
        ww = draw.textlength(word, font=f)
        sp = 0 if first_in_line else space_w_reg
        if cx + sp + ww > x + max_w and not first_in_line:
            # a capo
            cx = x
            y += lh
            sp = 0
            first_in_line = True
        if not first_in_line:
            cx += sp
        draw.text((cx, y), word, font=f, fill=col)
        cx += ww
        first_in_line = False
    y += lh
    return y


def draw_bottom_band(canvas, flyer, W, H):
    """Fascia inferiore a DUE COLONNE:
      - SINISTRA (~2/3): info evento allineate a sinistra
      - barra verticale terracotta divisoria
      - DESTRA (~1/3): foto ovale della conduttrice + nome/ruolo/note
    """
    draw = ImageDraw.Draw(canvas)

    # area verticale della fascia inferiore
    band_top = int(H * 0.685)
    band_bottom = int(H * 0.975)
    band_h = band_bottom - band_top

    # divisione 2/3 - 1/3
    left_margin = int(W * 0.06)
    split_x = int(W * 0.66)
    right_margin = int(W * 0.05)

    # linea decorativa orizzontale sopra tutta la fascia
    line_w = int(W * 0.88)
    lx0 = (W - line_w) / 2
    ly = band_top - int(H * 0.006)
    draw.line([(lx0, ly), (lx0 + line_w, ly)],
              fill=COL_BADGE_LINE, width=max(2, int(W * 0.0015)))

    # ---------------- COLONNA SINISTRA: info evento ----------------
    rows = flyer.get("info_evento") or []
    col_left_w = split_x - left_margin - int(W * 0.02)

    # font per i vari stili
    f_title = font_sans(int(W * 0.032), bold=True)
    f_title_b = f_title
    f_bold_r = font_sans(int(W * 0.0215), bold=True)
    f_bold_b = f_bold_r
    f_reg_r = font_sans(int(W * 0.0205))
    f_reg_b = font_sans(int(W * 0.0205), bold=True)
    f_soft_r = font_sans(int(W * 0.0185))
    f_soft_b = font_sans(int(W * 0.0185), bold=True)

    f_sub_r = font_sans(int(W * 0.024))
    f_sub_b = font_sans(int(W * 0.024), bold=True)

    STYLE_MAP = {
        # style -> (font_reg, font_bold, colore_base, colore_accento, factor)
        "title": (f_title, f_title_b, COL_TITLE, COL_TITLE, 1.25),
        "subtitle": (f_sub_r, f_sub_b, COL_DARK, COL_TITLE, 1.3),
        "bold": (f_bold_r, f_bold_b, COL_DARK, COL_TITLE, 1.3),
        "reg": (f_reg_r, f_reg_b, COL_DARK, COL_TITLE, 1.32),
        "soft": (f_soft_r, f_soft_b, COL_SOFT, COL_TITLE, 1.3),
    }
    # stili che vengono centrati nella colonna sinistra
    CENTERED = {"title", "subtitle"}

    # pre-misura l'altezza totale per centrare verticalmente il blocco
    def measure(rows):
        total = 0
        for r in rows:
            style = r.get("style", "reg")
            fr, fb, _, _, fac = STYLE_MAP[style]
            # stima righe con un wrap grezzo sul testo "pulito"
            clean = r["text"].replace("[[", "").replace("]]", "") \
                             .replace("{{", "").replace("}}", "")
            nlines = max(1, len(wrap(draw, clean, fr, col_left_w)))
            total += line_height(fb, fac) * nlines
            total += int(H * r.get("space_after", 0))
        return total

    total_h = measure(rows)
    y = band_top + max(0, (band_h - total_h) / 2)

    for r in rows:
        style = r.get("style", "reg")
        fr, fb, col_base, col_acc, fac = STYLE_MAP[style]
        tokens = parse_rich(r["text"])
        # le righe "title"/"subtitle" vengono CENTRATE nella colonna sinistra
        if style in CENTERED:
            clean = r["text"].replace("[[", "").replace("]]", "") \
                             .replace("{{", "").replace("}}", "")
            tw = draw.textlength(clean, font=fb)
            row_x = left_margin + max(0, (col_left_w - tw) / 2)
        else:
            row_x = left_margin
        y = draw_rich_line(draw, tokens, row_x, y, col_left_w,
                           fr, fb, col_base, col_acc, line_factor=fac)
        y += int(H * r.get("space_after", 0))

    # ---------------- BARRA VERTICALE divisoria ----------------
    bar_pad = int(H * 0.015)
    draw.line([(split_x, band_top + bar_pad), (split_x, band_bottom - bar_pad)],
              fill=COL_BADGE_LINE, width=max(2, int(W * 0.0015)))

    # ---------------- COLONNA DESTRA: conduttrice ----------------
    cond = flyer.get("conduttrice") or {}
    if cond:
        col_cx = (split_x + (W - right_margin)) / 2
        col_w = (W - right_margin) - split_x

        # foto ovale (o placeholder)
        photo_w = int(col_w * 0.66)
        photo_h = int(photo_w * 1.12)         # ovale verticale delicato
        photo_x = int(col_cx - photo_w / 2)
        photo_y = band_top + int(H * 0.015)

        foto_path = cond.get("foto")
        if foto_path and os.path.exists(foto_path):
            oval = oval_photo(Image.open(foto_path), (photo_w, photo_h))
            canvas.paste(oval, (photo_x, photo_y), oval)
        else:
            # placeholder ovale
            draw.ellipse([photo_x, photo_y, photo_x + photo_w,
                          photo_y + photo_h],
                         fill=(230, 224, 216), outline=COL_BADGE_LINE,
                         width=max(2, int(W * 0.02)))
            ph_f = font_sans(int(W * 0.020))
            ph_t = "foto"
            tw = draw.textlength(ph_t, font=ph_f)
            draw.text((col_cx - tw / 2, photo_y + photo_h / 2 - 10),
                      ph_t, font=ph_f, fill=COL_SOFT)

        # nome / ruolo / note sotto la foto
        ty = photo_y + photo_h + int(H * 0.018)
        col_pad = int(W * 0.015)
        inner_w = col_w - 2 * col_pad
        if cond.get("nome"):
            fn = font_sans(int(W * 0.021), bold=True)
            lines = wrap(draw, cond["nome"], fn, inner_w)
            ty = draw_multiline(draw, lines, fn, col_cx, ty, COL_TITLE,
                                align="center", line_factor=1.18)
            ty += int(H * 0.004)
        if cond.get("ruolo"):
            fr = font_serif(int(W * 0.0185), italic=True)
            lines = wrap(draw, cond["ruolo"], fr, inner_w)
            ty = draw_multiline(draw, lines, fr, col_cx, ty, COL_DARK,
                                align="center", line_factor=1.2)
            ty += int(H * 0.004)
        if cond.get("note"):
            # supporta {{...}} bold; centrato
            note_clean = cond["note"].replace("{{", "").replace("}}", "")
            is_bold = "{{" in cond["note"]
            fnt = font_sans(int(W * 0.019), bold=is_bold)
            lines = wrap(draw, note_clean, fnt, inner_w)
            ty = draw_multiline(draw, lines, fnt, col_cx, ty, COL_TITLE,
                                align="center", line_factor=1.18)


# ----------------------------------------------------------------------------
# COMPOSIZIONE
# ----------------------------------------------------------------------------

def compose(flyer, size):
    """Compone un flyer sul canvas della dimensione richiesta (W,H)."""
    W, H = size

    # --- sfondo: adatta l'illustrazione al canvas mantenendo il ratio ---
    bg_src = Image.open(flyer["background"]).convert("RGB")
    # riempi il canvas (cover) e ritaglia al centro
    scale = max(W / bg_src.width, H / bg_src.height)
    nw, nh = int(bg_src.width * scale), int(bg_src.height * scale)
    bg = bg_src.resize((nw, nh), Image.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    canvas = bg.crop((left, top, left + W, top + H)).convert("RGBA")

    draw = ImageDraw.Draw(canvas)
    cx = W / 2

    # --- logo + badge (alto sinistra) ---
    paste_logo(canvas, W, H)
    draw_badge(canvas, flyer.get("badge"), W, H)

    # --- blocco testo header (alto destra / centro) ---
    # Area testo header, allargata per ospitare righe lunghe su una sola riga.
    text_left = int(W * 0.30)
    text_right = W - int(W * 0.05)
    text_cx = (text_left + text_right) / 2
    max_text_w = text_right - text_left

    # Zona sicura: l'illustrazione inizia ~33% dell'altezza. L'header non deve
    # scendere oltre questo limite per non sovrapporsi ai ballerini.
    HEADER_BOTTOM = int(H * 0.325)

    y = int(H * 0.045)

    # occhiello
    if flyer.get("occhiello"):
        f = font_sans(int(W * 0.030), bold=True)
        lines = wrap(draw, flyer["occhiello"], f, max_text_w)
        y = draw_multiline(draw, lines, f, text_cx, y, COL_DARK,
                           align="center")
        y += int(H * 0.006)

    # titolo script (puo' essere su piu' righe via \n)
    if flyer.get("titolo"):
        f = font_script(int(W * 0.095))
        lines = wrap(draw, flyer["titolo"], f, max_text_w)
        y = draw_multiline(draw, lines, f, text_cx, y, COL_TITLE,
                           align="center", line_factor=0.98)
        # piccolo avvicinamento del sottotitolo al titolo
        y -= int(H * 0.004)

    # sottotitolo - AUTO-FIT su una riga
    if flyer.get("sottotitolo"):
        f, lines = fit_one_line(
            draw, flyer["sottotitolo"],
            lambda s: font_sans(s), int(W * 0.040), int(W * 0.026),
            max_text_w)
        y = draw_multiline(draw, lines, f, text_cx, y, COL_DARK,
                           align="center")
        y += int(H * 0.001)

    # descrizione (corsivo serif) - piu' grande, AUTO-FIT su una riga
    if flyer.get("descrizione"):
        f, lines = fit_one_line(
            draw, flyer["descrizione"],
            lambda s: font_serif(s, italic=True),
            int(W * 0.034), int(W * 0.022), max_text_w)
        y = draw_multiline(draw, lines, f, text_cx, y, COL_SOFT,
                           align="center")

    # --- fascia inferiore evento ---
    draw_bottom_band(canvas, flyer, W, H)

    return canvas.convert("RGB")


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for flyer in FLYERS:
        bg = flyer.get("background")
        if not bg or not os.path.exists(bg):
            print(f"[SALTO] Sfondo mancante per '{flyer.get('id')}': {bg}")
            continue
        for preset in OUTPUT_PRESETS:
            outdir = os.path.join(OUTPUT_DIR, preset["subdir"])
            os.makedirs(outdir, exist_ok=True)
            img = compose(flyer, preset["size"])

            # preset quadrato (Instagram): centra il flyer verticale su canvas 1:1
            sq = preset.get("square")
            if sq:
                # campiona il colore crema dall'angolo in alto del flyer
                cream = img.getpixel((5, 5))
                fit = img.copy()
                # scala per stare in altezza nel quadrato con un piccolo margine
                target_h = int(sq * 0.96)
                ratio = target_h / fit.height
                fit = fit.resize((int(fit.width * ratio), target_h),
                                 Image.LANCZOS)
                canvas_sq = Image.new("RGB", (sq, sq), cream)
                ox = (sq - fit.width) // 2
                oy = (sq - fit.height) // 2
                canvas_sq.paste(fit, (ox, oy))
                img = canvas_sq

            out = os.path.join(outdir, f"{flyer['id']}.png")
            img.save(out, "PNG", dpi=(preset["dpi"], preset["dpi"]))
            print(f"[OK] {preset['name']:9s} {img.size}  ->  {out}")
    print("\nFatto! Flyer generati in ./output/ (Stampa + Social)")


if __name__ == "__main__":
    main()
