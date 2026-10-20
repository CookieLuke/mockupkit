# 🎨 MockupKit

Crea immagini promozionali per il **Play Store** e **flyer** per eventi in pochi minuti, senza saper programmare.

Basta mettere i tuoi screenshot nella cartella, modificare un file di testo (YAML), e lanciare un comando. Il programma fa tutto il resto.

---

## ✨ Cosa genera

| Strumento | Cosa produce | Formato | Cartella |
|---|---|---|---|
| `genera_immagini.py` | Mockup per Play Store (smartphone + tablet) | PNG 1080×1920 / 1200×1920 | `output/` o custom |
| `Flyer/genera_flyer.py` | Flyer e locandine per eventi | PNG A4, Instagram, WhatsApp | `Flyer/output/` |

---

## 🚀 Avvio rapido

### 1. Installa le dipendenze (una volta sola)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Mac/Linux
# oppure: .venv\Scripts\activate  # Windows

pip install Pillow pyyaml
```

### 2. Genera i mockup

**Modalità semplice** – modifica un file YAML e lancia:

```bash
python genera_immagini.py --config config/ITA.yaml
```

**Genera solo un dispositivo** (più veloce per test):

```bash
python genera_immagini.py --config config/ITA.yaml --device "Smartphone"
```

**Vedi quali dispositivi sono nel config:**

```bash
python genera_immagini.py --config config/ITA.yaml --list-devices
```

**Modalità classica** (usa i testi hardcoded nel codice, senza YAML):

```bash
python genera_immagini.py
```

---

## 📁 Struttura del progetto

```
MockupKit/
│
├── config/                  ← ✏️ MODIFICA QUI i tuoi testi
│   ├── ITA.yaml             ← configurazione italiana
│   └── ENG.yaml             ← configurazione inglese
│
├── output/                  ← immagini generate (mockup ITA)
│   ├── Assets Smartphone/
│   ├── Assets Tablet 7/
│   └── Assets Tablet 10/
│
├── Assets/                  ← immagini generate (mockup ENG)
│   ├── ENG/
│   ├── ENG Tablet 7/
│   └── ENG Tablet 10/
│
├── Flyer/                   ← generatore di flyer
│   ├── genera_flyer.py
│   ├── assets/              ← loghi, foto, sfondi
│   └── output/              ← flyer generati
│
├── icone_altro/             ← logo app (IconMock.png)
├── genera_immagini.py       ← motore principale mockup
└── readme.md
```

---

## ✏️ Come personalizzare i mockup (senza toccare il codice)

Apri il file `config/ITA.yaml` con qualsiasi editor di testo (Blocco Note, TextEdit…).

Il file ha tre sezioni:

### 1. Brand
```yaml
logo: icone_altro/IconMock.png   # percorso al tuo logo PNG
```

### 2. Dispositivi
Puoi abilitare/disabilitare smartphone e tablet commentando con `#`:
```yaml
devices:
  - name: Smartphone
    canvas: [1080, 1920]
    frame: phone
    scale: 1.0
    outdir: output/Assets Smartphone

  # - name: Tablet 7         ← commenta per non generarlo
  #   canvas: [1200, 1920]
  #   ...
```

### 3. Slide (storyboard)
Ogni slide è un'immagine del Play Store. Modifica solo testi e screenshot:
```yaml
slides:
  - screenshot: mio_screenshot.png    # file nella cartella principale
    titolo: "IL MIO TITOLO"
    keyword: TITOLO                   # parola evidenziata in colore
    sottotitolo: "Breve descrizione."
```

> 💡 **Tip:** La `keyword` deve essere una parola contenuta nel `titolo` — verrà colorata automaticamente con il colore accent.

---

## 🗂 Aggiungere una nuova lingua

1. Copia `config/ITA.yaml` → `config/FR.yaml` (o la lingua che vuoi)
2. Modifica i testi nelle sezioni `slides`
3. Cambia le cartelle `outdir` (es. `output/Assets FR`)
4. Lancia:
```bash
python genera_immagini.py --config config/FR.yaml
```

---

## 🖼 Creare un flyer evento

Entra nella cartella `Flyer/` e modifica la sezione `FLYERS` in `genera_flyer.py`:

```python
FLYERS = [
    {
        "title":    "IL POTERE DELLA MUSICA",
        "subtitle": "Serata di Biodanza",
        "date":     "Venerdì 14 febbraio 2025",
        "time":     "ore 20:30",
        "place":    "Studio XYZ, Via Roma 10 – Torino",
        "teacher":  "con Sonia Trinchero",
        "photo":    os.path.join(ASSETS_DIR, "SoniaTrinchero.jpg"),
    },
]
```

Poi lancia:
```bash
cd Flyer
python genera_flyer.py
```

I flyer vengono generati in `Flyer/output/` nei formati: **A4, Instagram, WhatsApp/Social**.

---

## 🔠 Font richiesti

| Font | Usato in | Download |
|---|---|---|
| **Oswald** (variable) | Mockup Play Store | [Google Fonts](https://fonts.google.com/specimen/Oswald) |
| **Parisienne** | Flyer (titolo corsivo) | [Google Fonts](https://fonts.google.com/specimen/Parisienne) |
| **Lora** | Flyer (testo corpo) | [Google Fonts](https://fonts.google.com/specimen/Lora) |

Installa i `.ttf` nella cartella font del sistema:
- **Linux/Mac:** `~/.local/share/fonts/`
- **Windows:** doppio clic sul file → "Installa"

Se i font non vengono trovati, lo script usa un fallback automatico.

---

## ⚙️ Opzioni CLI complete

```
python genera_immagini.py [opzioni]

  --config FILE.yaml    -c   Usa un file di configurazione YAML
  --device NOME         -d   Genera solo questo dispositivo (es. "Smartphone")
  --list-devices             Elenca i dispositivi nel config e termina
  -h, --help                 Mostra questo aiuto
```

---

## 🐛 Problemi comuni

| Problema | Soluzione |
|---|---|
| `ModuleNotFoundError: PIL` | `pip install Pillow` |
| `ModuleNotFoundError: yaml` | `pip install pyyaml` |
| Font non trovato | Installa Oswald in `~/.local/share/fonts/` |
| Screenshot mancante | Controlla il nome file nello YAML (è case-sensitive) |
| Immagine nera o corrotta | Verifica che lo screenshot sia un PNG valido |

---

## 🗺 Roadmap futura

- [ ] Interfaccia web minima (drag & drop screenshot)
- [ ] Scelta del tema colori dallo YAML
- [ ] Supporto font custom da percorso locale nel config
- [ ] Template flyer multipli
