# Vom Projektordner zum GitHub-Repository

Ein Leitfaden für Einsteiger: Schritt für Schritt mit Git Bash unter Windows, von der Planung eines Projekts bis zur Veröffentlichung auf GitHub.

**[Leitfaden als PDF lesen](Leitfaden_GitHub_Repository.pdf)** · Version 1.1 · 19 Seiten

*Mit KI-Unterstützung erstellt.*

## Inhalt

1. So liest du diesen Leitfaden
2. Die wichtigsten Begriffe
3. Einmalig: GitHub-Konto vorbereiten
4. Einmalig: Git installieren und einrichten
5. Das Projekt planen, mit Strukturvorschlägen für sechs Projektarten
6. Das lokale Repository anlegen
7. Im Alltag: Änderungen festschreiben
8. Das Repo auf GitHub anlegen und hochladen
9. Weiterarbeiten: lokal und im Web
10. Einen fertigen Stand als Release veröffentlichen
11. Wenn etwas klemmt
12. Befehlsübersicht
13. Checkliste

## Dateien

| Datei | Zweck |
|---|---|
| `Leitfaden_GitHub_Repository.pdf` | Der fertige Leitfaden |
| `build_leitfaden.py` | Quelle: Python-Skript, das die PDF erzeugt und den gesamten Text enthält |
| `requirements.txt` | Benötigte Python-Bibliothek |

## PDF selbst erzeugen

Der Text des Leitfadens steht im Skript `build_leitfaden.py`. Änderungen am Inhalt erfolgen dort, die PDF wird anschließend neu erzeugt.

1. Python 3.10 oder neuer installieren.
2. ReportLab installieren:

   ```bash
   pip install -r requirements.txt
   ```

3. Die [DejaVu-Schriften](https://dejavu-fonts.github.io) herunterladen und diese sechs Dateien in einen Ordner `fonts/` neben dem Skript legen: `DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`, `DejaVuSans-Oblique.ttf`, `DejaVuSans-BoldOblique.ttf`, `DejaVuSansMono.ttf`, `DejaVuSansMono-Bold.ttf`. Alternativ findet das Skript die Schriften auch, wenn sie in Windows installiert sind.
4. Skript ausführen:

   ```bash
   python build_leitfaden.py
   ```

Der Ordner `fonts/` ist von Git ausgeschlossen, die Schriften gehören nicht zum Repository.

## Lizenz

Text und PDF stehen unter [CC BY 4.0](LICENSE): Weitergabe und Bearbeitung sind erlaubt, solange der Urheber genannt wird.
