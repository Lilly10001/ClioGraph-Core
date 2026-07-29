# ClioGraph 🏛️📊 — Historische Graphen-Analyse & Graph-RAG
In der vorliegenden Beschreibung wird zur Vereinfachung die männliche Sprachform verwendet. Es sind immer Männer und Frauen gleichberechtigt mitgemeint.

**Ein dynamisch erweiterbares GUI-Basisframework und Analyse-Arbeitsplatz für historische Netzwerke in den Digital Humanities.** (nicht promotionsrelevant, daher Open Source)

ClioGraph trennt die Benutzeroberfläche strikt von der Forschungslogik eines wissenschaftlichen Arbeitsplatzes der Digital Humanities und Digital History. Über ein rein deklaratives JSON-Schema gesteuert, können Historiker, Geisteswissenschaftler und Entwickler dynamisch Registerkarten, Schaltflächen und Makros im laufenden Betrieb erzeugen, umbauen und lokalisieren, bevor die tiefe Fachlogik zur Wissens-Extraktion greift. Dies dient zur strikten Einhaltung der Programmierprinzipien von n-Tier, OOP, Kapselung, dynamischer Erweiterung, Mehrsprachigkeit just-in-time und direktem Zugriff auf den Code bei dem Hinzufügen benutzerdefinierter:
- Hauptmenüs, Items/Schaltflächen (einfache Action-Schaltfläche und Submenüs) und Tabs/Register hinzufügen 
- über die beiden Sidebars "System-Designer" und "IDE-Designer bzw. Entwicklertool" in Anlehnung an IDE die Elemente hinzufügen, umbenennen, platzieren und löschen
- den Items/Schaltflächen des Hauptmenüs benutzerdefinierte Makro-Befehle zuordnen (Sidebar/IDE-Designer/)
- den Tabs/Registern manuell Formularsteuerlemente hinzufügen und mit rechter Mausklick-Menüführung steuern bzw. mit dem GenAI-Formulardesigner Formular automatsich generieren
- unter Datei den TranslationSprachenService für Mehrsprachigkeit und automatischer Ollama-Übersetzung nutzen just-in-time. Als Defaultsprachen sind "de" und "en" gesetzt
- Tools zur automatisierten Dokumentation und Konsistenzsicherung der Sprachdateien

---

## 🚀 Geplante Funktionen & Fachlogik für den wiss. Arbeitsplatz ClioGraph (Promotionsvorhaben, daher erst mit Dissertation zu veröffentlichen)
- **Wissens-Extraktion:** Automatische Entitäten- und Beziehungs-Extraktion aus Quellentexten via lokalem Ollama.
- **Netzwerkanalyse:** Berechnung und Visualisierung historischer Netzwerk-Metriken.
- **Graph-RAG Training:** Interaktive Abfragen an die historischen Daten über LLM-Prompting.
- **Graph Machine Learning:** Prädiktive Struktur-Analyse mittels Graph Neural Networks (GNN).

---

## 🛠️ Hauptmerkmale des GUI-Basisframeworks
- **Deklaratives UI-Schema:** Die gesamte Benutzeroberfläche wird dynamisch über eine zentrale JSON-Konfiguration (`UI_SCHEMA`) gesteuert.
- **Strict Bilingualism (i18n):** Volle, gleichwertige Unterstützung für Deutsch und Englisch (und vorbereitet für historische Forschungssprachen).
- **IDE-Designer (Developer Tools):** Visuelle Werkzeuge direkt im Interface, um Formular-Steuerelemente zur Laufzeit zu erstellen, zu verschieben und zweisprachig umzubenennen.
- **Transaktionales Undo/Redo:** Ein Zustandssystem sichert UI-Änderungen über Checkpoints ab.
- **Saubere Kapselung (Once-Only / Command Pattern):** UI-Aktionen rufen isolierte, zustandslose Befehlsklassen auf.

---

## 📂 Projektstruktur (n-tier Architektur)
- `gui/` — Presentation Layer (Reine PyQt6 Oberfläche, WidgetFactory, IDE-Tools).
- `business/` — Business Logic Layer (BLL) für Commands, Makros und typsichere Datenmodelle.
- `database/` — Data Access Layer (DAL) für die spätere Kùzu-Graphdatenbank.
- `llm_ml/` — Machine Learning Layer für GNNs und Prompting-Dienste.
- `infrastructure/` — Technische Hilfsdienste (I18N-Sprachdienst, System-Infrastruktur, Konfigurationen).
- `json_storage/` — Datenhaltung für Lokalisierungen und persistente GUI-Zustände.

---

## ⚙️ Installation & Setup

### 1. Repository klonen & vorbereiten
```bash
git clone https://github.com
cd clioGraph
```

### 2. Virtuelle Umgebung einrichten & aktivieren
```bash
# Virtuelle Umgebung erstellen
python -m venv .venv

# Aktivieren (Windows)
.venv\Scripts\activate
# Aktivieren (macOS/Linux)
source .venv/bin/activate
```

### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 4. Lokales LLM starten (Voraussetzung für spätere Fachlogik)
Stellen Sie sicher, dass Ollama auf Ihrem System installiert ist und läuft:
```bash
ollama run llama3:science
```

### 5. Anwendung starten
```bash
python main.py
```

---

## 🤝 Mitwirken (Contribution)
Beiträge zur Erweiterung des GUI-Frameworks oder zur Implementierung neuer wissenschaftlicher Makros sind herzlich willkommen! Bitte beachten Sie, dass neue GUI-Elemente immer zweisprachig über das integrierte IDE-Kontextmenü registriert werden müssen. Kontakt: info@cliograph.ch. Die Webseite www.cliograph.ch ist in Arbeit.

## @2026 Copyright - Haftungsausschluss - Verwendung für wissenschaftliche und Schulungszwecke - Disclaimer
THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This code is provided for educational/utility purposes only without any warranty. Use at your own risk.

@2026 Copyright ClioGraph Schweiz
