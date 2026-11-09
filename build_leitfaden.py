# build_leitfaden.py
# Erzeugt den Leitfaden "Vom Projektordner zum GitHub-Repository" als PDF.
#
# Voraussetzungen:
#   - Python 3.10 oder neuer
#   - ReportLab:  pip install -r requirements.txt
#   - DejaVu-Schriften (DejaVuSans*.ttf, DejaVuSansMono*.ttf) im Ordner fonts/
#     oder systemweit installiert. Download: https://dejavu-fonts.github.io
#
# Aufruf:  python build_leitfaden.py
# Ergebnis: Leitfaden_GitHub_Repository.pdf im selben Ordner

import os
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, KeepTogether, Preformatted)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Leitfaden_GitHub_Repository.pdf"
VERSION = "1.1"

FONT_FILES = {
    "Sans": "DejaVuSans.ttf",
    "Sans-B": "DejaVuSans-Bold.ttf",
    "Sans-I": "DejaVuSans-Oblique.ttf",
    "Sans-BI": "DejaVuSans-BoldOblique.ttf",
    "Mono": "DejaVuSansMono.ttf",
    "Mono-B": "DejaVuSansMono-Bold.ttf",
}

FONT_DIRS = [
    HERE / "fonts",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts",
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
    Path("/usr/share/fonts/truetype/dejavu"),
    Path.home() / "Library" / "Fonts",
]


def find_font(filename):
    for d in FONT_DIRS:
        f = d / filename
        if f.is_file():
            return f
    return None


missing = []
for name, filename in FONT_FILES.items():
    path = find_font(filename)
    if path is None:
        missing.append(filename)
    else:
        pdfmetrics.registerFont(TTFont(name, str(path)))
if missing:
    sys.exit("Schriften nicht gefunden: " + ", ".join(missing) +
             "\nBitte die DejaVu-Schriften in den Ordner fonts/ legen (siehe README).")

addMapping("Sans", 0, 0, "Sans"); addMapping("Sans", 1, 0, "Sans-B")
addMapping("Sans", 0, 1, "Sans-I"); addMapping("Sans", 1, 1, "Sans-BI")
addMapping("Mono", 0, 0, "Mono"); addMapping("Mono", 1, 0, "Mono-B")

ACCENT = colors.HexColor("#1f4e79")
CODEBG = colors.HexColor("#f2f4f7")
CODEBD = colors.HexColor("#c9d1db")
TIPBG = colors.HexColor("#eaf4ea")
TIPBD = colors.HexColor("#5a9a5a")
WARNBG = colors.HexColor("#fdf1e6")
WARNBD = colors.HexColor("#d4822a")
GREY = colors.HexColor("#555555")

ss = {}
ss["body"] = ParagraphStyle("body", fontName="Sans", fontSize=10, leading=14.5, spaceAfter=6)
ss["h1"] = ParagraphStyle("h1", fontName="Sans-B", fontSize=17, leading=21, textColor=ACCENT,
                          spaceBefore=4, spaceAfter=10, keepWithNext=1)
ss["h2"] = ParagraphStyle("h2", fontName="Sans-B", fontSize=12.5, leading=16, textColor=ACCENT,
                          spaceBefore=10, spaceAfter=5, keepWithNext=1)
ss["h3"] = ParagraphStyle("h3", fontName="Sans-B", fontSize=11, leading=14, textColor=colors.HexColor("#2e6da4"), spaceBefore=9, spaceAfter=4, keepWithNext=1)
ss["small"] = ParagraphStyle("small", parent=ss["body"], fontSize=8.5, leading=11.5, textColor=GREY)
ss["bullet"] = ParagraphStyle("bullet", parent=ss["body"], leftIndent=14, bulletIndent=3, spaceAfter=3)
ss["box"] = ParagraphStyle("box", parent=ss["body"], spaceAfter=0)
ss["cell"] = ParagraphStyle("cell", fontName="Sans", fontSize=9, leading=12)
ss["cellb"] = ParagraphStyle("cellb", fontName="Sans-B", fontSize=9, leading=12, textColor=colors.white)
ss["cellmono"] = ParagraphStyle("cellmono", fontName="Mono", fontSize=8.5, leading=11.5)
ss["code"] = ParagraphStyle("code", fontName="Mono", fontSize=8.6, leading=12)
ss["title"] = ParagraphStyle("title", fontName="Sans-B", fontSize=26, leading=32, textColor=ACCENT,
                             alignment=TA_LEFT, spaceAfter=10)
ss["subtitle"] = ParagraphStyle("subtitle", fontName="Sans", fontSize=13, leading=18, textColor=GREY,
                                spaceAfter=20)
ss["check"] = ParagraphStyle("check", parent=ss["body"], leftIndent=18, firstLineIndent=-18, spaceAfter=4)
ss["toc1"] = ParagraphStyle("toc1", fontName="Sans", fontSize=10.5, leading=17, leftIndent=0)

story = []
W = A4[0] - 40 * mm


def h1(t):
    p = Paragraph(t, ss["h1"]); p._toc = t; story.append(p)


def h2(t):
    story.append(Paragraph(t, ss["h2"]))


KEEP = {"next": False}
ss["bodykeep"] = ParagraphStyle("bodykeep", parent=ss["body"], keepWithNext=1)


def h3(t):
    story.append(Paragraph(t, ss["h3"])); KEEP["next"] = True


def p(t):
    st = ss["bodykeep"] if KEEP["next"] else ss["body"]
    KEEP["next"] = False
    story.append(Paragraph(t, st))


def bl(items):
    for i in items:
        story.append(Paragraph(i, ss["bullet"], bulletText="•"))
    story.append(Spacer(1, 3))


def code(t):
    pre = Preformatted(t.strip("\n"), ss["code"])
    tb = Table([[pre]], colWidths=[W])
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODEBG),
        ("BOX", (0, 0), (-1, -1), 0.6, CODEBD),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb); story.append(Spacer(1, 7))


def box(t, kind="tip"):
    bg, bd, label = (TIPBG, TIPBD, "Tipp") if kind == "tip" else (WARNBG, WARNBD, "Achtung")
    para = Paragraph(f"<b>{label}:</b> {t}", ss["box"])
    tb = Table([[para]], colWidths=[W])
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, bd),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb); story.append(Spacer(1, 8))


def table(head, rows, widths, mono_first=False):
    data = [[Paragraph(h, ss["cellb"]) for h in head]]
    for r in rows:
        data.append([Paragraph(c, ss["cellmono"] if (mono_first and i == 0) else ss["cell"])
                     for i, c in enumerate(r)])
    tb = Table(data, colWidths=[w * W for w in widths], repeatRows=1)
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CODEBG]),
        ("GRID", (0, 0), (-1, -1), 0.4, CODEBD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(tb); story.append(Spacer(1, 9))


def m(t):  # inline mono
    return f'<font name="Mono" size="9">{t}</font>'


# ---------------------------------------------------------------- Titel
story.append(Spacer(1, 45 * mm))
story.append(Paragraph("Vom Projektordner<br/>zum GitHub-Repository", ss["title"]))
story.append(Paragraph("Ein Leitfaden für Einsteiger: Schritt für Schritt mit Git Bash unter Windows,"
                       " von der Planung bis zur Veröffentlichung", ss["subtitle"]))
story.append(Spacer(1, 10 * mm))
p("<b>Was du am Ende kannst:</b> einen lokalen Projektordner sauber vorbereiten, daraus ein Git-Repository machen, "
  "Änderungen nachvollziehbar festschreiben, das Projekt auf GitHub hochladen, dort weiterpflegen und "
  "einen fertigen Stand als Release veröffentlichen, ohne dabei Zugangsdaten oder deine private "
  "Mailadresse preiszugeben.")
p("<b>Voraussetzungen:</b> ein Windows-Rechner, ein GitHub-Konto und etwas Neugier. Vorkenntnisse in Git "
  "brauchst du nicht.")
story.append(Spacer(1, 30 * mm))
story.append(Paragraph(f"Version {VERSION} · November 2026", ss["small"]))
story.append(PageBreak())

# ---------------------------------------------------------------- Inhalt
story.append(Paragraph("Inhalt", ss["h1"]))
toc = TableOfContents()
toc.levelStyles = [ss["toc1"]]
toc.dotsMinLevel = 0
story.append(toc)
story.append(PageBreak())

# ---------------------------------------------------------------- 0
h1("1  So liest du diesen Leitfaden")
p("Der Leitfaden ist so aufgebaut, dass jedes Kapitel auf dem vorigen aufbaut. Die ersten Kapitel erledigst du "
  "nur einmal pro Rechner, ab Kapitel 5 folgt der Ablauf, den du für jedes neue Projekt wiederholst. "
  "Kapitel 10 und 11 sind Nachschlagewerk für den Fall, dass etwas klemmt.")
h2("Platzhalter")
p("Alles in spitzen Klammern ersetzt du durch deine eigenen Angaben, und zwar <b>ohne</b> die Klammern:")
table(["Platzhalter", "Bedeutung", "Beispiel"], [
    [m("&lt;GITHUB-NAME&gt;"), "Dein Benutzername auf GitHub", m("tomlahr")],
    [m("&lt;ID&gt;"), "Die Zahl vor deiner GitHub-Ersatzadresse (Kapitel 3)", m("12345678")],
    [m("&lt;PROJEKT&gt;"), "Name des Projektordners und späteren Repos, ohne Leerzeichen", m("Pico-Wetterstation")],
    [m("&lt;DATEI&gt;"), "Name einer Datei im Projekt", m("README.md")],
    [m("&lt;NACHRICHT&gt;"), "Kurze Beschreibung einer Änderung", m("README um Verdrahtung ergänzt")],
], [0.27, 0.43, 0.30])
h2("Befehle eingeben")
p("Alle grau hinterlegten Zeilen gibst du in der <b>Git Bash</b> ein und bestätigst jede mit Enter. "
  "Zeilen, die mit " + m("#") + " beginnen, sind Kommentare zur Erklärung; die musst du nicht eintippen.")
code("""
# Das ist ein Kommentar
git status
""")
box("In der Git Bash funktioniert Strg+V oft nicht. Einfügen geht mit <b>Umschalt+Einfg</b> oder "
    "<b>Rechtsklick → Paste</b>. Zum Kopieren markierst du Text einfach mit der Maus.")
box("Mehrere lesende Befehle (" + m("status") + ", " + m("log") + ", " + m("diff") + ") darfst du "
    "gemeinsam einfügen. Befehle, die etwas verändern oder löschen, gibst du einzeln ein und liest die "
    "Ausgabe, bevor der nächste folgt.", "warn")

# ---------------------------------------------------------------- 2
h1("2  Die wichtigsten Begriffe")
p("Git und GitHub sind zwei verschiedene Dinge, die zusammenarbeiten:")
bl(["<b>Git</b> ist ein Programm auf deinem Rechner. Es merkt sich jede Version deiner Dateien.",
    "<b>GitHub</b> ist eine Website, auf der du diese Versionsgeschichte online ablegst, sicherst und "
    "anderen zeigen kannst."])
table(["Begriff", "Bedeutung im Alltag"], [
    ["Repository (Repo)", "Ein Projektordner, dessen Geschichte Git verwaltet. Die Geschichte liegt im "
     "versteckten Unterordner " + m(".git") + "."],
    ["Commit", "Ein festgeschriebener Zwischenstand mit Nachricht, Autor und Datum. Wie ein Foto deines "
     "Projekts zu einem Zeitpunkt."],
    ["Staging (" + m("git add") + ")", "Das Vormerken von Änderungen für den nächsten Commit. Du entscheidest, "
     "was in das nächste „Foto“ kommt."],
    ["Branch", "Eine Entwicklungslinie. Für den Einstieg genügt der Hauptzweig " + m("main") + "."],
    ["Remote / " + m("origin"), "Die Verbindung zum Repo auf GitHub. " + m("origin") + " ist ihr üblicher Name."],
    ["Push", "Lokale Commits zu GitHub hochladen."],
    ["Fetch / Pull", "Stand von GitHub holen. Fetch schaut nur nach, Pull übernimmt die Änderungen auch."],
    ["Tag / Release", "Eine dauerhafte Markierung eines Commits als Version, z. B. " + m("v1.0") + "."],
], [0.25, 0.75])
p("Der Weg einer Änderung sieht immer gleich aus:")
code("""
Datei ändern  →  git add  →  git commit  →  git push  →  GitHub
 (Arbeitsordner)  (vormerken)  (festschreiben)  (hochladen)
""")

# ---------------------------------------------------------------- 3
h1("3  Einmalig: GitHub-Konto vorbereiten")
p("Git schreibt in jeden Commit eine Mailadresse, und die ist in öffentlichen Repos für jeden lesbar. "
  "Programme suchen GitHub gezielt nach solchen Adressen ab. Deshalb nutzt du eine Ersatzadresse, "
  "die GitHub dir kostenlos bereitstellt.")
h2("Schritt 3.1: Ersatzadresse aktivieren")
bl(["Auf GitHub oben rechts auf dein Profilbild → <b>Settings</b>.",
    "Links <b>Emails</b> wählen.",
    "Häkchen bei <b>Keep my email addresses private</b> setzen.",
    "Die angezeigte Adresse der Form " + m("&lt;ID&gt;+&lt;GITHUB-NAME&gt;@users.noreply.github.com") +
    " notieren.",
    "Häkchen bei <b>Block command line pushes that expose my email</b> setzen. Dann lehnt GitHub jeden "
    "Upload ab, in dem versehentlich deine echte Adresse steckt."])
box("Die Ersatzadresse ist dafür gedacht, öffentlich zu sein. Du musst sie nicht geheim halten.")

# ---------------------------------------------------------------- 4
h1("4  Einmalig: Git installieren und einrichten")
h2("Schritt 4.1: Git für Windows installieren")
p("Lade „Git for Windows“ von " + m("git-scm.com") + " herunter und installiere es. Die vorgeschlagenen "
  "Einstellungen im Installationsassistenten kannst du übernehmen. Danach findest du im Startmenü die "
  "<b>Git Bash</b>, ein Konsolenfenster ähnlich wie unter Linux.")
code("""
# In der Git Bash: Läuft Git?
git --version
""")
h2("Schritt 4.2: Identität festlegen")
p("Diese Angaben gelten für alle Repos auf diesem Rechner (" + m("--global") + "). Du machst das nur einmal.")
code("""
git config --global user.name "<GITHUB-NAME>"
git config --global user.email "<ID>+<GITHUB-NAME>@users.noreply.github.com"
""")
box("Trage hier <b>niemals</b> deine echte Mailadresse ein. Sie stünde sonst dauerhaft in jedem Commit, "
    "auch nach späterem Löschen der Dateien.", "warn")
h2("Schritt 4.3: Weitere Grundeinstellungen")
code("""
# Hauptzweig heißt "main" wie auf GitHub
git config --global init.defaultBranch main

# Windows- und Linux-Zeilenenden automatisch angleichen
git config --global core.autocrlf true

# Beim Abholen von GitHub zusammenführen statt nachfragen
git config --global pull.rebase false

# Kontrolle: alles anzeigen
git config --global --list
""")
p("In der Liste sollten Name, Ersatzadresse, " + m("main") + ", " + m("true") + " und " + m("false") +
  " auftauchen. Steht dort eine echte Mailadresse, wiederholst du einfach den Befehl aus Schritt 4.2.")
h2("Schritt 4.4: Arbeitsordner anlegen")
p("Lege einen festen Ordner für alle Repos an, zum Beispiel " + m("C:\\GitHub") + ". Er sollte "
  "<b>nicht</b> in einem Cloud-Ordner wie OneDrive liegen, weil sich Synchronisierung und Git gegenseitig "
  "stören können.")
box("Ist an deinem Rechner der Windows-Administratorschutz aktiv, prüfe, wem der Ordner gehört: "
    "Rechtsklick → Eigenschaften → Sicherheit → Erweitert → <b>Besitzer</b>. Dort sollte dein eigenes "
    "Benutzerkonto stehen. Sonst meldet Git später „dubious ownership“ (siehe Kapitel 11).", "warn")
h2("Schritt 4.5: In der Git Bash zurechtfinden")
table(["Aufgabe", "So geht's"], [
    ["Pfad angeben", "Windows " + m("C:\\GitHub") + " heißt in der Bash " + m("/c/GitHub")],
    ["Ordner wechseln", m("cd /c/GitHub/&lt;PROJEKT&gt;")],
    ["Ordnerinhalt anzeigen", m("ls") + " (versteckte Dateien mit " + m("ls -a") + ")"],
    ["Namen ergänzen", "Anfang tippen, dann <b>Tab-Taste</b>"],
    ["Leerzeichen im Namen", "Pfad in Anführungszeichen: " + m('cd "/c/GitHub/Mein Ordner"')],
    ["Bash direkt im Ordner öffnen", "Explorer: Rechtsklick auf den Ordner → Weitere Optionen anzeigen → "
     "<b>Open Git Bash here</b>"],
], [0.30, 0.70])

# ---------------------------------------------------------------- 5
h1("5  Das Projekt planen")
p("Ein gut geplanter Ordner erspart dir später Aufräumarbeit. Überlege vor dem ersten Commit, was "
  "hinein gehört und was nicht.")
h2("Schritt 5.1: Namen festlegen")
bl(["Keine Leerzeichen, keine Umlaute. Bindestriche trennen Wörter: " + m("Pico-Wetterstation") + ".",
    "Ordner und späteres Repo heißen gleich. GitHub erlaubt ohnehin keine Leerzeichen in Repo-Namen."])
h2("Schritt 5.2: Die Projektart bestimmen")
p("Nicht jedes Repo enthält Programmcode. GitHub eignet sich für alles, was aus Dateien besteht und sich "
  "im Lauf der Zeit verändert: Texte, Anleitungen, Daten, Einstellungen. Je nach Art des Inhalts bewährt "
  "sich eine andere Ordnerstruktur. Bestimme deshalb zuerst, welche Art von Projekt du anlegst.")
table(["Projektart", "Beispiele", "Typische Lizenz", "Sichtbarkeit"], [
    ["A  Längeres Schriftwerk", "Buch, Abhandlung, Handbuch", "CC BY 4.0", "Öffentlich oder privat"],
    ["B  Kurzes Dokument", "Artikel, Précis, Bedienungs- oder Einrichtungsanleitung", "CC BY 4.0",
     "Meist öffentlich"],
    ["C  DIY-Projekt mit Code", "Pico, ESP32, Raspberry Pi", "MIT", "Meist öffentlich"],
    ["D  Daten-Repo", "Messreihen, Verbrauchswerte", "CC BY 4.0 oder keine", "Meist privat"],
    ["E  Konfigurationssammlung", "Home Assistant, ESPHome, Skripte", "MIT oder keine", "Fast immer privat"],
    ["F  Wissenssammlung", "Notizen, Spickzettel, Linklisten", "CC BY 4.0 oder keine", "Öffentlich oder privat"],
], [0.27, 0.33, 0.19, 0.21])
p("Zwei Begriffe aus der Tabelle kurz erklärt: <b>MIT</b> ist eine Lizenz für Software. Sie erlaubt jedem, "
  "den Code zu nutzen und zu verändern, solange dein Name erhalten bleibt. <b>CC BY 4.0</b> (Creative Commons, "
  "Namensnennung) leistet dasselbe für Texte, Bilder und Daten. Für Texte passt sie besser als eine "
  "Software-Lizenz. „Keine“ heißt: Bei privaten Repos, die niemand außer dir sieht, brauchst du keine Lizenz.")
box("Ein paar Regeln gelten für alle Arten: Datei- und Ordnernamen klein, ohne Leerzeichen und Umlaute. "
    "Wo die Reihenfolge zählt, stellst du Nummern voran: " + m("01-einleitung.md") + ", "
    + m("02-grundlagen.md") + ". Und Texte schreibst du in <b>Markdown</b> (" + m(".md") + ") statt in Word: "
    "Git zeigt dann jede Änderung zeilengenau, bei Word-Dateien sieht es nur „Datei geändert“.")

h3("A  Längeres Schriftwerk: Buch, Abhandlung, Handbuch")
p("Jedes Kapitel bekommt eine eigene Datei. So siehst du in der Versionsgeschichte sofort, in welchem "
  "Kapitel du was geändert hast, und behältst auch bei hundert Seiten den Überblick.")
code("""
<BUCHTITEL>/
├── README.md              # Worum geht es? Inhaltsverzeichnis mit Links
├── LICENSE                # z. B. CC BY 4.0
├── .gitattributes         # Bilder und PDFs als binär kennzeichnen
├── kapitel/
│   ├── 00-vorwort.md
│   ├── 01-einleitung.md
│   ├── 02-grundlagen.md
│   └── 03-praxis.md
├── bilder/
│   ├── abb-01-uebersicht.png
│   └── abb-02-aufbau.jpg
└── quellen/
    └── literatur.md       # Quellenangaben, Links
""")
bl(["Die README dient als Inhaltsverzeichnis. Links auf Kapitel schreibst du relativ: "
    + m("[Einleitung](kapitel/01-einleitung.md)") + ". GitHub macht daraus klickbare Verweise.",
    "Bilder bindest du im Kapitel ein mit " + m("![Beschreibung](../bilder/abb-01-uebersicht.png)") +
    ". Die zwei Punkte bedeuten „eine Ordnerebene höher“.",
    "Die fertige PDF-Fassung legst du am besten <b>nicht</b> ins Repo, sondern hängst sie an ein Release "
    "(Kapitel 10). Git speichert eine PDF bei jeder Änderung komplett neu, das bläht das Repo auf."])

h3("B  Kurzes Dokument: Artikel, Précis, Anleitung")
p("Für Texte, die auf wenige Seiten passen, reicht eine flache Struktur ohne Unterordner für Kapitel.")
code("""
<ANLEITUNG>/
├── README.md              # Kurzbeschreibung, Version, Link zum Dokument
├── LICENSE                # z. B. CC BY 4.0
├── .gitattributes         # *.pdf binary, *.png binary
├── anleitung.md           # der eigentliche Text
├── befehle.txt            # optional: Befehle zum Kopieren
└── bilder/
    ├── schritt-01.png
    └── schritt-02.png
""")
bl(["Bei einem Précis oder Artikel genügt oft sogar nur " + m("README.md") + " plus " + m("artikel.md") + ".",
    "Die Versionsnummer gehört an eine feste Stelle, etwa oben in die README. Fertige Stände "
    "veröffentlichst du als Release.",
    "Bildschirmfotos vor dem Hochladen prüfen: Benutzernamen, Gerätenamen, Netzwerknamen oder IP-Adressen "
    "lassen sich leicht übersehen."])
box("Eine PDF-Fassung im Repo ist bei kurzen Dokumenten vertretbar. Dann aber unbedingt "
    + m("*.pdf binary") + " in die " + m(".gitattributes") + " eintragen, sonst kann Git die Datei "
    "beschädigen (Schritt 6.3).", "warn")

h3("C  DIY-Projekt mit Code: Mikrocontroller, Raspberry Pi")
p("Hier trennt der Ordner " + m("src") + " sauber, was auf das Gerät kommt, von dem, was nur der "
  "Dokumentation dient. Wer dein Projekt nachbauen will, kopiert einfach den Inhalt von " + m("src") + ".")
code("""
<PROJEKT>/
├── README.md              # Hardware, Verdrahtung, Installation, Bedienung
├── LICENSE                # z. B. MIT
├── .gitignore             # secrets.py, vom Gerät erzeugte Dateien
├── .gitattributes
├── src/                   # alles, was aufs Gerät kommt
│   ├── main.py
│   ├── config.py          # Einstellungen, Pins, Kalibrierung
│   ├── secrets_example.py  # Vorlage mit Platzhaltern
│   └── lib/               # nur falls auch auf dem Gerät vorhanden
├── docs/
│   ├── verdrahtung.png
│   └── aufbau-foto.jpg
└── hardware/              # optional
    ├── schaltplan.pdf
    └── gehaeuse.stl       # 3D-Druck-Vorlage
""")
bl(["Die Struktur in " + m("src") + " entspricht genau dem Stammverzeichnis auf dem Gerät.",
    "Dateien, die das Gerät im Betrieb selbst anlegt (Messwert-Speicher, letzte Einstellungen), gehören in "
    "die " + m(".gitignore") + ". Sie beschreiben den Zustand deines Geräts, nicht den Code.",
    "Arbeitest du mit Werkzeugen wie PlatformIO oder der Arduino-IDE, geben diese eine eigene Struktur vor "
    "(etwa " + m("platformio.ini") + ", " + m("src/") + ", " + m("include/") + ", " + m("lib/") + "). "
    "Folge dann deren Vorgabe, statt eine eigene zu erfinden.",
    "Datenblätter und fremde Bibliotheken verlinkst du in der README, statt sie hochzuladen."])

h3("D  Daten-Repo: Messreihen, Verbrauchswerte")
p("Git eignet sich gut, um Datenreihen zu pflegen, weil jede neue oder korrigierte Zeile in der "
  "Versionsgeschichte sichtbar wird. Wichtigster Teil ist dabei die Beschreibung, woher die Zahlen stammen.")
code("""
<DATENREIHE>/
├── README.md              # Herkunft, Methodik, Lücken, Einheiten
├── .gitattributes         # *.png binary, *.xlsx binary
├── daten/
│   ├── 2025.csv
│   └── 2026.csv
└── auswertung/
    ├── auswertung.py      # optional: Skript, das die Grafiken erzeugt
    ├── verlauf-2025.png
    └── verlauf-2026.png
""")
bl(["<b>CSV statt Excel</b> als eigentliche Datenquelle: CSV ist reiner Text, Git zeigt jede geänderte Zeile. "
    "Eine Excel-Datei mit Formeln darf zusätzlich existieren, ist aber nicht die „Wahrheit“.",
    "In der README festhalten: Woher kommen die Werte? Welcher Zeitraum? Welche Einheit? Wo gibt es Lücken "
    "oder Schätzungen? Ohne diese Angaben weißt du ein Jahr später nicht mehr, was die Zahlen bedeuten.",
    "Grafiken (PNG) sind Momentaufnahmen. Kommen neue Daten hinzu, musst du sie neu erzeugen.",
    "GitHub warnt bei Dateien über 50 MB und lehnt Dateien über 100 MB ab. Große Datenmengen teilst du "
    "deshalb in Jahres- oder Monatsdateien auf."])
box("Nutzungsdaten verraten indirekt viel über dein Leben, etwa wann du zu Hause bist oder verreist. "
    "Solche Repos stellst du auf <b>Private</b>.", "warn")

h3("E  Konfigurationssammlung: Home Assistant, ESPHome, Skripte")
p("Wer seine Einstellungen in Git ablegt, kann jede Änderung nachvollziehen und nach einem misslungenen "
  "Experiment auf den letzten funktionierenden Stand zurückgehen.")
code("""
<KONFIGURATION>/
├── README.md              # Welches Gerät, welche Version, was steckt wo
├── .gitignore             # secrets.yaml, Datenbanken, Logs
├── homeassistant/
│   ├── configuration.yaml
│   ├── automations.yaml
│   ├── scripts.yaml
│   ├── secrets_example.yaml   # Vorlage mit Platzhaltern
│   └── packages/
├── esphome/
│   ├── wohnzimmer-sensor.yaml
│   └── secrets_example.yaml
└── skripte/
    └── backup.sh
""")
bl(["Zugangsdaten liegen bei Home Assistant und ESPHome in " + m("secrets.yaml") + ". Diese Datei gehört "
    "immer in die " + m(".gitignore") + ", ins Repo nur eine Vorlage mit Platzhaltern.",
    "Datenbanken und Protokolle (" + m("*.db") + ", " + m("*.log") + ") ebenfalls in die "
    + m(".gitignore") + ": Sie ändern sich ständig und sind kein Bestandteil der Konfiguration.",
    "Gerätenamen, Raumbezeichnungen und IP-Adressen beschreiben deine Wohnung. Deshalb solche Repos "
    "<b>immer privat</b> halten, auch wenn keine Passwörter darin stehen."])

h3("F  Wissenssammlung: Notizen, Spickzettel, Linklisten")
p("Die einfachste Art: einzelne Markdown-Dateien zu einem Thema, die mit der Zeit wachsen. GitHub zeigt "
  "jede Datei formatiert an, mit Überschriften, Tabellen und klickbaren Links.")
code("""
<THEMA>/
├── README.md              # Übersicht mit Links zu allen Seiten
├── grundlagen.md
├── befehle.md
├── links.md
└── bilder/
    └── beispiel.png
""")
bl(["Querverweise zwischen Seiten funktionieren relativ: " + m("[Befehle](befehle.md)") + ".",
    "Kleine, häufige Commits lohnen sich hier besonders. So siehst du später, wann du was gelernt oder "
    "korrigiert hast.",
    "Wächst die Sammlung über ein Dutzend Seiten, gliedere sie in Unterordner nach Teilthemen."])

h2("Schritt 5.3: Was gehört nicht in ein Repo?")
table(["Nicht hochladen", "Stattdessen"], [
    ["Zugangsdaten (WLAN, Passwörter, Tokens)", "Eigene Datei wie " + m("secrets.py") + ", in "
     + m(".gitignore") + " eintragen; ins Repo nur eine Vorlage " + m("secrets_example.py") + " mit Platzhaltern"],
    ["Private Angaben (Router, Zeiten, Wohnung)", "Private Notizen außerhalb des Repos"],
    ["ZIP-Archive mit Code", "Entpackte Dateien. GitHub kann in ZIPs nicht hineinschauen."],
    ["Fremde Datenblätter und Handbücher", "In der README verlinken"],
    ["Automatisch erzeugte Dateien", "In " + m(".gitignore") + " eintragen"],
], [0.38, 0.62])
box("Was einmal committet und hochgeladen ist, bleibt in der Versionsgeschichte abrufbar, auch wenn du die "
    "Datei später löschst. Ein versehentlich veröffentlichtes Passwort musst du deshalb <b>sofort ändern</b>.",
    "warn")
h2("Schritt 5.4: README vorbereiten")
p("Die " + m("README.md") + " zeigt GitHub auf der Startseite des Repos an. Sie sollte mindestens "
  "beantworten: Was ist das Projekt? Was brauche ich dafür? Wie setze ich es ein? Ein einfaches Grundgerüst:")
code("""
# <PROJEKT>

Kurze Beschreibung in ein bis zwei Sätzen.

## Hardware / Voraussetzungen

## Installation

## Bedienung

## Lizenz

MIT, siehe LICENSE
""")

# ---------------------------------------------------------------- 6
h1("6  Das lokale Repository anlegen")
p("Jetzt wird aus dem Ordner ein Git-Repository. Die Reihenfolge ist wichtig: Die Schutzdateien kommen "
  "<b>vor</b> dem ersten Commit.")
h2("Schritt 6.1: In den Ordner wechseln und Git starten")
code("""
cd /c/GitHub/<PROJEKT>
git init
""")
p("Git meldet „Initialized empty Git repository“. In der Eingabezeile erscheint jetzt " + m("(main)") +
  ", das Zeichen, dass du dich in einem Repo befindest.")
h2("Schritt 6.2: .gitignore anlegen")
p("Diese Datei listet alles, was Git grundsätzlich ignorieren soll. Passe die Liste an dein Projekt an:")
code("""
cat > .gitignore << 'EOF'
# Zugangsdaten
secrets.py
*.env

# Automatisch erzeugt
__pycache__/
*.log

# Systemdateien
Thumbs.db
desktop.ini
.DS_Store
EOF
""")
p("Der Befehl " + m("cat &gt; DATEI &lt;&lt; 'EOF'") + " schreibt alle folgenden Zeilen bis zum Wort "
  + m("EOF") + " in die Datei. Du kannst die Datei genauso gut mit einem Texteditor anlegen.")
h2("Schritt 6.3: .gitattributes anlegen")
p("Wegen " + m("core.autocrlf") + " passt Git Zeilenenden an. Bei Binärdateien wie PDFs oder Bildern "
  "würde das die Datei beschädigen. Diese Regeln verhindern das:")
code("""
cat > .gitattributes << 'EOF'
* text=auto
*.pdf binary
*.png binary
*.jpg binary
*.zip binary
*.xlsx binary
EOF
""")
h2("Schritt 6.4: Lizenz anlegen")
p("Ohne Lizenz darf rechtlich niemand deine Inhalte weiterverwenden, auch wenn sie öffentlich sind. Welche "
  "Lizenz passt, steht in der Tabelle in Schritt 5.2: MIT für Code, CC BY 4.0 für Texte und Daten. Am einfachsten legst du sie später auf GitHub an "
  "(Kapitel 8). Alternativ kopierst du den Lizenztext von " + m("choosealicense.com") +
  " in eine Datei " + m("LICENSE") + " und ergänzt Jahr und Namen.")
h2("Schritt 6.5: Kontrollieren, was Git sieht")
code("""
git status
""")
p("Unter „Untracked files“ listet Git alle Dateien, die es noch nicht verwaltet. Prüfe die Liste genau: "
  "Taucht dort " + m("secrets.py") + " auf, stimmt etwas mit der " + m(".gitignore") + " nicht. Dann erst "
  "korrigieren, nicht weitermachen.")
h2("Schritt 6.6: Der erste Commit")
code("""
# Alle Dateien vormerken
git add .

# Vorgemerktes anzeigen (grün = wird festgeschrieben)
git status

# Festschreiben
git commit -m "Erster Stand: Projektstruktur, README, Schutzdateien"
""")
p("Der Punkt in " + m("git add .") + " steht für „alles im aktuellen Ordner“, abzüglich dessen, was "
  + m(".gitignore") + " ausschließt.")
h2("Schritt 6.7: Den Commit prüfen")
code("""
git log --format="%h  %an <%ae>  %ad  %s" --date=short
""")
p("Die Zeile zeigt Kurzkennung, Name, <b>Mailadresse</b>, Datum und Nachricht. Steht dort deine "
  "Ersatzadresse, ist alles richtig.")

# ---------------------------------------------------------------- 7
h1("7  Im Alltag: Änderungen festschreiben")
p("Solange dein Projekt lokal reift, wiederholst du diesen kleinen Kreislauf, so oft du willst.")
h2("Schritt 7.1: Der Arbeitszyklus")
code("""
# 1. Was hat sich geändert?
git status

# 2. Was genau? (q beendet die Anzeige)
git diff

# 3. Vormerken: einzelne Datei oder alles
git add <DATEI>
git add .

# 4. Festschreiben
git commit -m "<NACHRICHT>"
""")
h2("Schritt 7.2: Gute Commit-Nachrichten")
p("Deine Versionsgeschichte ist nur so nützlich wie ihre Nachrichten. Schreib so, dass du in einem Jahr "
  "noch weißt, was du warum geändert hast. Deutsch ist völlig in Ordnung.")
table(["Gut", "Nicht hilfreich"], [
    ["„TEMP_OFFSET auf -3.2 nach Abgleich mit Referenzsensor“", "„Änderung“"],
    ["„README um Verdrahtungstabelle ergänzt“", "„Update“"],
    ["„WLAN-Wiederverbindung nach 3 Fehlversuchen“", "„Fix“"],
], [0.6, 0.4])
h2("Schritt 7.3: Einen Fehler rückgängig machen")
table(["Situation", "Befehl"], [
    ["Änderung an einer Datei verwerfen (noch nicht vorgemerkt)", m("git restore &lt;DATEI&gt;")],
    ["Datei aus dem Vormerken nehmen", m("git restore --staged &lt;DATEI&gt;")],
    ["Letzte Commit-Nachricht korrigieren (noch nicht hochgeladen)",
     m('git commit --amend -m "&lt;NACHRICHT&gt;"')],
], [0.55, 0.45])
box(m("git restore") + " verwirft Änderungen endgültig. Im Zweifel vorher den Ordner kopieren.", "warn")

# ---------------------------------------------------------------- 8
h1("8  Das Repo auf GitHub anlegen und hochladen")
p("Ist das Projekt reif genug, verbindest du es mit GitHub.")
h2("Schritt 8.1: Leeres Repo auf GitHub erstellen")
bl(["Auf GitHub oben rechts <b>+</b> → <b>New repository</b>.",
    "<b>Repository name:</b> genau " + m("&lt;PROJEKT&gt;") + ", wie dein lokaler Ordner.",
    "<b>Description:</b> ein Satz, was das Projekt ist.",
    "<b>Sichtbarkeit:</b> zunächst <b>Private</b> wählen. Umstellen auf Public geht jederzeit später.",
    "<b>Keine</b> Häkchen bei „Add a README file“, „.gitignore“ oder „license“ setzen.",
    "<b>Create repository</b>."])
box("Das Repo muss <b>leer</b> sein. Legt GitHub eine README an, existieren online und lokal zwei "
    "verschiedene erste Commits, und der erste Upload wird abgelehnt.", "warn")
p("GitHub zeigt dir danach eine Seite mit Befehlen. Du brauchst davon nur die Adresse in der Form "
  + m("https://github.com/&lt;GITHUB-NAME&gt;/&lt;PROJEKT&gt;.git") + ".")
h2("Schritt 8.2: Lokales Repo mit GitHub verbinden")
code("""
git remote add origin https://github.com/<GITHUB-NAME>/<PROJEKT>.git

# Kontrolle
git remote -v
""")
p("Die Kontrolle zeigt zweimal die Adresse, einmal mit „fetch“ (holen) und einmal mit „push“ (hochladen).")
h2("Schritt 8.3: Erster Upload")
code("""
git push -u origin main
""")
p("Beim allerersten Upload öffnet sich ein Fenster des <b>Git Credential Managers</b>. Du meldest dich im "
  "Browser bei GitHub an und erlaubst den Zugriff. Danach merkt sich Windows die Anmeldung; Passwörter "
  "musst du nirgends von Hand eintragen. Das " + m("-u") + " verknüpft deinen lokalen Zweig dauerhaft mit "
  "GitHub, künftig reicht ein einfaches " + m("git push") + ".")
h2("Schritt 8.4: Ergebnis auf GitHub prüfen")
bl(["Lade die Repo-Seite neu. Deine Dateien und die README erscheinen.",
    "Fehlt " + m("secrets.py") + "? Gut, genau so soll es sein.",
    "Rechts erscheint nach kurzer Zeit unter „Languages“ die erkannte Programmiersprache."])
h2("Schritt 8.5: Repo vervollständigen (Weboberfläche)")
table(["Aufgabe", "So geht's"], [
    ["Lizenz", "Add file → Create new file → Name " + m("LICENSE") + " → Choose a license template → "
     "passende Lizenz wählen (Schritt 5.2) → Jahr und Name eintragen → Commit changes. Fehlt CC BY 4.0 in der Auswahl, legst du die Datei mit dem Text von " + m("choosealicense.com/licenses/cc-by-4.0") + " an."],
    ["Beschreibung und Topics", "Zahnrad neben <b>About</b>. Topics nur Kleinbuchstaben, Ziffern, "
     "Bindestriche; einzeln eintippen und mit Enter bestätigen."],
], [0.25, 0.75])
box("Hast du auf GitHub etwas geändert (z. B. die Lizenz angelegt), hole diese Änderung vor dem "
    "Weiterarbeiten auf deinen Rechner: " + m("git pull") + ". Mehr dazu in Kapitel 9.")

# ---------------------------------------------------------------- 9
h1("9  Weiterarbeiten: lokal und im Web")
p("Ab jetzt existiert dein Projekt an zwei Orten. Die wichtigste Regel: Beide Stände müssen "
  "zusammenpassen.")
h2("Schritt 9.1: Vor jeder Arbeitssitzung")
code("""
cd /c/GitHub/<PROJEKT>
git fetch
git status
""")
p("Meldet " + m("git status") + " „Your branch is behind“, liegt online Neueres, etwa aus der "
  "Weboberfläche. Dann holst du es ab:")
code("""
git pull
""")
h2("Schritt 9.2: Nach getaner Arbeit")
code("""
git add .
git commit -m "<NACHRICHT>"
git push
""")
box("Arbeitest du auch über die Weboberfläche oder von einem zweiten Gerät aus, gewöhne dir an: "
    "<b>Vorher pullen, nachher pushen.</b> Dann laufen die Stände nie auseinander.")
h2("Schritt 9.3: Von Private auf Public umstellen")
p("Ist das Projekt reif für die Öffentlichkeit:")
bl(["Vorher die gesamte Geschichte prüfen, denn sie wird mit veröffentlicht: " +
    m('git log --format="%h  %ae  %s"') + ". Keine echte Mailadresse, keine Zugangsdaten?",
    "Auf GitHub: <b>Settings</b> → ganz unten <b>Danger Zone</b> → <b>Change visibility</b> → Public."])

# ---------------------------------------------------------------- 10
h1("10  Einen fertigen Stand als Release veröffentlichen")
p("Ein Release markiert einen Commit dauerhaft als Version. Besucher sehen sofort, welche Fassung "
  "die aktuelle ist, und spätere Änderungen überschreiben sie nicht.")
h2("Schritt 10.1: Vorbereitung")
bl(["Alles committet und hochgeladen? " + m("git status") + " meldet „up to date“ und „working tree clean“.",
    "Dokumente auf Entwurfsvermerke prüfen, Versionsnummern abgleichen."])
h2("Schritt 10.2: Release anlegen (Weboberfläche)")
bl(["Auf der Repo-Startseite rechts unter <b>Releases</b> → <b>Create a new release</b>.",
    "<b>Choose a tag</b> → z. B. " + m("v1.0") + " eintippen → <b>Create new tag on publish</b>.",
    "<b>Release title:</b> z. B. „Version 1.0“.",
    "<b>Release notes:</b> was enthalten ist und was sich geändert hat.",
    "Optional: Dateien für Leser ohne Git-Kenntnisse (z. B. eine PDF) unter <b>Attach binaries</b> anhängen.",
    "<b>Release label</b> auf „None“ lassen; „Pre-release“ nur für unfertige Stände.",
    "<b>Publish release</b>."])
p("Nach dem Release holst du die neue Markierung auch auf deinen Rechner:")
code("""
git fetch --tags
""")

# ---------------------------------------------------------------- 11
h1("11  Wenn etwas klemmt")
p("Die häufigsten Meldungen und was sie bedeuten:")
probs = [
    ("„detected dubious ownership in repository“",
     "Der Ordner gehört nicht deinem Benutzerkonto, häufig nach Anlegen mit Administratorrechten.",
     "Besitzer des Ordners auf das eigene Konto ändern (Schritt 4.4). Notlösung: "
     + m("git config --global --add safe.directory C:/GitHub/&lt;PROJEKT&gt;")),
    ("„! [rejected] main -&gt; main (fetch first)“",
     "Online liegen Commits, die du lokal nicht hast.",
     m("git pull") + ", dann erneut " + m("git push")),
    ("„GH007: Your push would publish a private email address“",
     "Ein Commit trägt deine echte Mailadresse.",
     "Schritt 4.2 wiederholen. Betrifft es nur den letzten Commit: "
     + m("git commit --amend --reset-author --no-edit") + ", dann " + m("git push")),
    ("„LF will be replaced by CRLF“",
     "Hinweis zur Angleichung der Zeilenenden. Bei Textdateien harmlos.",
     "Erscheint die Meldung bei einer PDF oder einem Bild: " + m(".gitattributes") + " prüfen (Schritt 6.3) "
     "und die Datei mit " + m("git restore &lt;DATEI&gt;") + " zurückholen, nicht committen."),
    ("„No such file or directory“ bei " + m("cd"),
     "Pfad falsch geschrieben oder Leerzeichen im Namen.",
     "Pfad in Anführungszeichen setzen, Tab-Ergänzung nutzen."),
    ("„fatal: not a git repository“",
     "Du bist nicht im Projektordner.",
     m("cd /c/GitHub/&lt;PROJEKT&gt;")),
    ("„remote origin already exists“",
     "Die Verbindung zu GitHub ist schon eingerichtet.",
     "Mit " + m("git remote -v") + " prüfen. Falsche Adresse korrigieren: "
     + m("git remote set-url origin &lt;ADRESSE&gt;")),
    ("Anzeige hängt, unten steht „:“ oder „(END)“",
     "Git zeigt eine lange Ausgabe seitenweise an.",
     "Taste <b>q</b> beendet die Anzeige."),
]
table(["Meldung", "Ursache", "Lösung"], [list(x) for x in probs], [0.30, 0.30, 0.40])
h2("Notfall: Zugangsdaten versehentlich committet")
p("<b>Noch nicht hochgeladen</b> und nur im letzten Commit:")
code("""
# Datei aus Git entfernen, aber auf der Festplatte behalten
git rm --cached secrets.py

# In .gitignore eintragen, falls noch nicht geschehen
echo "secrets.py" >> .gitignore
git add .gitignore

# Letzten Commit ohne die Datei neu schreiben
git commit --amend --no-edit
""")
p("<b>Bereits hochgeladen:</b> Betroffenes Passwort <b>sofort ändern</b>. Das ist der einzige wirklich "
  "sichere Schritt, denn wer die Daten schon abgegriffen hat, behält sie. Die Bereinigung der "
  "Versionsgeschichte ist danach ein zweiter, aufwendigerer Schritt, für den du dir Unterstützung holen "
  "solltest.")
box("Vor jedem Eingriff in die Versionsgeschichte den ganzen Projektordner kopieren, inklusive "
    "des versteckten " + m(".git") + "-Ordners: " + m('cp -r "&lt;PROJEKT&gt;" "_Backup_&lt;PROJEKT&gt;"'), "warn")

# ---------------------------------------------------------------- 12
h1("12  Befehlsübersicht")
table(["Befehl", "Wirkung"], [
    ["git status", "Zustand: geänderte und neue Dateien, Abstand zu GitHub"],
    ["git init", "Ordner zum Repo machen"],
    ["git add &lt;DATEI&gt;  /  git add .", "Datei / alles für den nächsten Commit vormerken"],
    ['git commit -m "&lt;NACHRICHT&gt;"', "Vorgemerktes festschreiben"],
    ["git diff", "Änderungen zeilengenau anzeigen"],
    ['git log --format="%h  %an &lt;%ae&gt;  %ad  %s" --date=short', "Commits mit Autor, Mail, Datum"],
    ["git remote add origin &lt;ADRESSE&gt;", "Verbindung zu GitHub herstellen"],
    ["git remote -v", "Verbindung anzeigen"],
    ["git push -u origin main", "Erster Upload"],
    ["git push", "Lokale Commits hochladen"],
    ["git fetch", "Online-Stand ansehen, ohne lokal etwas zu ändern"],
    ["git pull", "Online-Stand holen und übernehmen"],
    ["git restore &lt;DATEI&gt;", "Lokale Änderung verwerfen"],
    ["git restore --staged &lt;DATEI&gt;", "Datei aus dem Vormerken nehmen"],
    ["git rm --cached &lt;DATEI&gt;", "Datei aus Git entfernen, auf Platte behalten"],
    ["git config --global --list", "Einstellungen anzeigen"],
], [0.50, 0.50], mono_first=True)

# ---------------------------------------------------------------- Checkliste
story.append(PageBreak())
h1("13  Checkliste")
p("Zum Abhaken für jedes neue Projekt. Die ersten beiden Blöcke erledigst du nur einmal pro Rechner.")


def check(title, items):
    block = [Paragraph(title, ss["h2"])]
    for i in items:
        block.append(Paragraph("☐  " + i, ss["check"]))
    story.append(KeepTogether(block))


check("Einmalig: GitHub-Konto", [
    "„Keep my email addresses private“ aktiviert, Ersatzadresse notiert",
    "„Block command line pushes that expose my email“ aktiviert"])
check("Einmalig: Rechner", [
    "Git für Windows installiert, " + m("git --version") + " funktioniert",
    m("user.name") + " und " + m("user.email") + " (Ersatzadresse!) gesetzt",
    m("init.defaultBranch main") + ", " + m("core.autocrlf true") + ", " + m("pull.rebase false") + " gesetzt",
    "Arbeitsordner " + m("C:\\GitHub") + " angelegt, außerhalb von OneDrive, Besitzer ist das eigene Konto"])
check("Planung", [
    "Projektname ohne Leerzeichen und Umlaute festgelegt",
    "Projektart bestimmt, Ordnerstruktur und Lizenz passend gewählt (Schritt 5.2)",
    "Zugangsdaten nur in " + m("secrets.py") + ", Vorlage " + m("secrets_example.py") + " mit Platzhaltern",
    "Keine privaten Angaben, keine ZIPs, keine fremden Handbücher im Ordner",
    "README mit Beschreibung, Voraussetzungen, Installation"])
check("Lokales Repo", [
    m("git init") + " ausgeführt",
    m(".gitignore") + " angelegt, " + m("secrets.py") + " eingetragen",
    m(".gitattributes") + " angelegt, Binärdateien eingetragen",
    m("git status") + " geprüft: keine Zugangsdaten unter „Untracked files“",
    "Erster Commit erstellt",
    m("git log") + " geprüft: Ersatzadresse im Commit"])
check("Veröffentlichung", [
    "Leeres Repo auf GitHub erstellt, ohne README/Lizenz-Häkchen, zunächst Private",
    m("git remote add origin") + " ausgeführt, mit " + m("git remote -v") + " geprüft",
    m("git push -u origin main") + " erfolgreich, Anmeldung per Browser erledigt",
    "Dateien auf GitHub sichtbar, " + m("secrets.py") + " fehlt",
    "Lizenz angelegt, Beschreibung und Topics gesetzt",
    "Lokal " + m("git pull") + " nach Änderungen auf GitHub"])
check("Öffentlich machen und Release", [
    "Gesamte Geschichte auf Mailadressen und Zugangsdaten geprüft",
    "Sichtbarkeit auf Public umgestellt",
    "Dokumente ohne Entwurfsvermerk, Versionsnummern stimmen",
    "Release mit Tag, Titel und Beschreibung veröffentlicht",
    "Bei Bedarf PDF oder andere Dateien als Download angehängt"])
check("Im Alltag", [
    "Vor der Arbeit: " + m("git fetch") + ", " + m("git status") + ", ggf. " + m("git pull"),
    "Nach der Arbeit: " + m("git add") + ", " + m("git commit") + " mit aussagekräftiger Nachricht, "
    + m("git push")])


# ---------------------------------------------------------------- Build
class Doc(BaseDocTemplate):
    def __init__(self, fn):
        super().__init__(fn, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                         topMargin=20 * mm, bottomMargin=20 * mm,
                         title="Vom Projektordner zum GitHub-Repository",
                         author="Thomas Lahr", subject="Leitfaden für Git Bash unter Windows")
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="p", frames=[fr], onPage=self.deco)])

    def deco(self, c, d):
        if d.page == 1:
            return
        c.saveState()
        c.setFont("Sans", 8); c.setFillColor(GREY)
        c.drawString(20 * mm, 12 * mm, "Vom Projektordner zum GitHub-Repository")
        c.drawRightString(A4[0] - 20 * mm, 12 * mm, f"Seite {d.page}")
        c.setStrokeColor(CODEBD); c.setLineWidth(0.5)
        c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
        c.restoreState()

    def afterFlowable(self, f):
        if hasattr(f, "_toc"):
            self.notify("TOCEntry", (0, f._toc, self.page))


if __name__ == "__main__":
    Doc(str(OUTPUT)).multiBuild(story)
    print(f"Fertig: {OUTPUT.name}")
