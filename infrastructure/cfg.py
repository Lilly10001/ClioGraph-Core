# Datei: infrastructure/cfg.py
"""Infrastructure Layer: Globale Konfiguration und Übersetzungs-Wörterbuch (I18N) für ClioGraph"""

import os
import sys
from pathlib import Path
import importlib
import pkgutil
import inspect

# Fügt das Hauptverzeichnis zum Suchpfad von Python hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from business.commands.cmd_base import UICommand

APP_NAME = "ClioGraph"

# UI-Format für den Fehlerdienst
ERROR_UI_FORMAT = "{prefix} ? Details: {message}"

def get_user_data_dir() -> Path:
    """Ermittelt den offiziellen, beschreibbaren Anwendungsordner des Betriebssystems."""
    if sys.platform == "win32":
        # Windows: C:\Users\Name\AppData\Roaming\ClioGraph
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    elif sys.platform == "darwin":
        # macOS: /Users/Name/Library/Application Support/ClioGraph
        base_dir = Path.home() / "Library/Application Support"
    else:
        # Linux: /home/Name/.config/cliograph
        base_dir = Path.home() / ".config"
    
    data_dir = base_dir / APP_NAME
    # Erstellt den Ordner automatisch, falls er noch nicht existiert
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

# Zentrale, dynamische Pfade definieren
USER_DATA_PATH = get_user_data_dir()
DB_PATH = str(USER_DATA_PATH / "cliograph_db")
LOG_FILE_PATH = str(USER_DATA_PATH / "cliograph_system.log")

# Ermittelt dynamisch das Hauptverzeichnis deines Projekts (ClioGraph/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ZENTRALE PFAD-DEFINITION FÜR ALLERLEI JSON-DATEIEN (Egal auf welchem Laufwerk oder PC!)
JSON_STORAGE_DIR = str(PROJECT_ROOT / "json_storage")
JSON_MENU_FILE = os.path.join(JSON_STORAGE_DIR, "dynamic_menu.json")

# =====================================================================
# DYNAMISCHER ORDNER FÜR DIE SPRACH-DATEIEN DER FORSCHER
# =====================================================================
JSON_LOCALES_DIR = os.path.join(JSON_STORAGE_DIR, "locales")

# Sicherheits-Check: Falls der Ordner jemals fehlen sollte, erstellt Python ihn automatisch
if not os.path.exists(JSON_LOCALES_DIR):
    os.makedirs(JSON_LOCALES_DIR, exist_ok=True)

# Sicherheits-Check: Falls der Ordner im Projektverzeichnis fehlt, erstellt Python ihn automatisch
if not os.path.exists(JSON_STORAGE_DIR):
    os.makedirs(JSON_STORAGE_DIR, exist_ok=True)


# 1. UNVERÄNDERLICHE MASTER-SPRACHEN (Systemschutz vor Löschung)
MASTER_LANGUAGES = ["de", "en"]

# =====================================================================
# GLOBALER EXLOSIVER EDITOR-BEFEHL (Kapselung für die Community)
# =====================================================================
EXTERNAL_EDITOR_COMMAND = "code"

# =====================================================================
# GLOBALE ANWENDUNGSEINSTELLUNGEN (MINIMALES AUSGANGSGERÜST)
# =====================================================================
APP_CONFIG = {
    "version": "1.0.0",
    "default_language": "de",
    "supported_languages": ["de", "en"],
    "default_model": "llama3:latest",
    "max_main_menus": 8,       # Reduziert von 10 auf exakt 8 Hauptmenüs (inkl. Datei)
    "max_tabs": 10,           # Begrenzung auf maximal 10 geöffnete Registerkarten
}



# 2. AKTIVE ANZEIGELUSTE FÜR DIE GUI (Wird später im Betrieb erweitert)
AVAILABLE_LANGUAGES = [
    {"name": "Deutsch", "code": "de"},
    {"name": "English", "code": "en"}
]


# =====================================================================
# ZENTRALES WÖRTERBUCH FÜR DIE INTERNATIONALISIERUNG (I18N)
# =====================================================================
I18N = {
    # --- Visual Studio Style Start-Texte (GUI-BasisFramework) ---
    "tabs.welcome.title": {
        "de": "Willkommen",
        "en": "Welcome"
    },
    "dialog.welcome.headline": {
        "de": "Exemplarische Vorgehensweisen",
        "en": "Exemplary Procedures"
    },
       
    # --- Allgemeine Applikations-Texte ---
    "app.title": {
        "de": "ClioGraph ➖ Historische Graphen-Analyse & Graph-RAG",
        "en": "ClioGraph ➖ Historical Graph Analytics & Graph-RAG"
    },
    "app.status.ready": {
        "de": "System-Infrastruktur geladen. Bereit.",
        "en": "System infrastructure loaded. Ready."
    },
    "menu.language": {
        "de": "Sprache",
        "en": "Language"
    },
    
    # --- Das geschützte Basis-Menü ---
    "menu.file": {
        "de": "Datei",
        "en": "File"
    },
    "menu.file.language": {
        "de": "Sprache wechseln",
        "en": "Change Language"
    },
    "menu.file.exit": {
        "de": "Beenden",
        "en": "Exit"
    },

     "menu.file.reset_system": {
        "de": "System-Infrastruktur zurücksetzen",
        "en": "Reset System Infrastructure"
    },
    "dialog.reset.title": {
        "de": "System zurücksetzen",
        "en": "Reset System"
    },
    "dialog.reset.text": {
        "de": "Möchten Sie das System wirklich auf die Werkseinstellungen zurücksetzen?\nAlle dynamischen Menüs und hinzugefügten Sprachen werden archiviert.",
        "en": "Do you really want to reset the system to default settings?\nAll dynamic menus and added languages will be archived."
    },

    "menu.file.export": {
        "de": "Projekt exportieren",
        "en": "Export Project"
    },
    
    # --- Die 8 Hauptmenü-Übersetzungen (Vorbereitung für Forscher) ---
    "menu.sources": { "de": "Quellenverwaltung", "en": "Source Management" },
    "menu.database": { "de": "Datenbank", "en": "Database" },
    "menu.apis": { "de": "APIs", "en": "APIs" },
    "menu.register": { "de": "Register", "en": "Tabs" },
    "menu.visualization": { "de": "Visualisierung", "en": "Visualization" },
    "menu.community": { "de": "Community", "en": "Community" },
    "menu.help": { "de": "Hilfe", "en": "Help" },

    # Tab/Register-Einträge

    # --- System-Designer Tab-Steuerung ---
    "sidebar.tab.move_left": {
        "de": "Nach links",
        "en": "Move Left"
    },
    "sidebar.tab.move_right": {
        "de": "Nach rechts",
        "en": "Move Right"
    },

    # --- Die 4 neuen, strukturierten Fach-Registerkarten (Zweisprachig) ---
    "tabs.extraction.title": {"de": "🚀 Wissensextraktion", "en": "🚀 Knowledge Extraction"},
    "tabs.network.title": {"de": "🕸️ Netzwerkanalyse", "en": "🕸️ Network Analysis"},
    "tabs.graphrag.title": {"de": "🧠 GraphRAG & LLM", "en": "🧠 GraphRAG & LLM"},
    "tabs.ml.title": {"de": "📊 Machine Learning", "en": "📊 Machine Learning"},
    
    # --- Formularfelder & Platzhalter (Eingaben und Viewer) ---
    "fields.source_placeholder": {"de": "Fügen Sie hier den historischen Quellentext ein...", "en": "Paste the historical source text here..."},
    "fields.output_placeholder": {"de": "Hier erscheint das extrahierte Wissensnetzwerk als JSON...", "en": "The extracted knowledge network will appear here as JSON..."},
    
    "fields.network_filter_placeholder": {"de": "Knoten- oder Kantenfilter (z.B. Person, Ort)...", "en": "Node or edge filter (e.g., Person, Location)..."},
    "fields.network_log_placeholder": {"de": "Netzwerkanalyse-Metriken (Zentralitätswerte, Cluster)...", "en": "Network analysis metrics (centrality values, clusters)..."},
    
    "fields.graphrag_query_placeholder": {"de": "Stellen Sie eine historische Frage an Ihren Wissensgraphen...", "en": "Ask a historical question to your knowledge graph..."},
    "fields.graphrag_answer_placeholder": {"de": "Die synthetisierte GraphRAG-Antwort mit Quellenbelegen...", "en": "The synthesized GraphRAG answer with source citations..."},
    
    "fields.ml_features_placeholder": {"de": "Eingabe-Vektor für Klassifikation oder Mustererkennung...", "en": "Input vector for classification or pattern recognition..."},
    
    # --- Interaktions-Schaltflächen (Buttons) ---
    "buttons.start_extraction": {"de": "Extraktion starten", "en": "Start Extraction"},
    "buttons.render_network": {"de": "Netzwerk generieren", "en": "Render Network"},
    "buttons.query_graph": {"de": "Wissensgraph abfragen", "en": "Query Knowledge Graph"},
    "buttons.train_model": {"de": "Modell trainieren", "en": "Train Model"},

    # --- Standard-Platzhalter für leere Befehle ---
    "dummy.test_feature": {
        "de": "Dynamisches Test-Feature",
        "en": "Dynamic Test Feature"
    },
    
    # --- Sidebar Haupt-Buttons ---
    "sidebar.btn.system_designer": {
        "de": "⚙️ System-Designer",
        "en": "⚙️ System Designer"
    },
    "sidebar.btn.developer_tools": {
        "de": "💼 Entwicklertools",
        "en": "💼 Developer Tools"
    },

    # --- IDE-Formularbaukasten ---
    "ide.headline.vba": {
        "de": "🗔 Formular-Steuerelemente",
        "en": "🗔 Form Controls"
    },
    "ide.label.widget_type": {
        "de": "Objekt-Typ auswählen:",
        "en": "Select Object Type:"
    },
    "ide.label.element_id": {
        "de": "Technische ID (eindeutig):",
        "en": "Technical ID (unique):"
    },
    "ide.btn.insert_widget": {
        "de": "Baustein auf Tab platzieren",
        "en": "Insert Control on Tab"
    },

    # --- Generischer Open-Source GenAI Formular-Builder ---
    "ide.headline.genai": {
        "de": "🧬 GenAI Formular-Builder",
        "en": "🧬 GenAI Formular Builder"
    },
    "ide.placeholder.prompt": {
        "de": "Beschreiben Sie die gewünschten Felder (z.B. Name, Adresse, Button)...",
        "en": "Describe the desired fields (e.g., name, address, button)..."
    },
    "ide.btn.generate": {
        "de": "Layout generieren",
        "en": "Generate Layout"
    },

    # --- Zentraler Fehlerdienst (errors.py) ---
    "error.validation": { "de": "[Validierung]", "en": "[Validation]" },
    "error.graph_data": { "de": "[Daten-Fehler]", "en": "[Data Error]" },
    "error.database": { "de": "[Datenbank-Fehler]", "en": "[Database Error]" },
    "error.llm": { "de": "[KI-Dienst-Fehler]", "en": "[AI Service Error]" },
    "error.generic": { "de": "[Anwendungs-Fehler]", "en": "[Application Error]" },
    "error.unknown": { "de": "[Kritischer Systemfehler]", "en": "[Critical System Error]" }
}


def discover_all_commands(filter_prefix: str = None) -> dict:
    """Sucht alle Makro-Klassen im commands-Ordner."""
    pool = {}
    import business.commands as cmd_pkg
    
    for _, mod_name, is_pkg in pkgutil.iter_modules(cmd_pkg.__path__):
        if is_pkg or mod_name == "cmd_base":
            continue
        
        if filter_prefix:
            allowed_modules = [f"cmd_{filter_prefix}", "cmd_dummy"]
            if mod_name not in allowed_modules:
                continue
        
        mod = importlib.import_module(f"business.commands.{mod_name}")
        
        for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
            if issubclass(cls, UICommand) and cls is not UICommand:
                display_name = f"[{mod_name}.py] -> {cls_name}"
                pool[display_name] = cls()
                
    return pool

# =====================================================================
# DAS GENERISCHE GUI-SCHEMA FÜR CLIOGRAPH (AUSGANGSGERÜST)
# =====================================================================

# =====================================================================
# DAS GENERISCHE GUI-SCHEMA FÜR CLIOGRAPH (REPARIERTES AUSGANGSGERÜST)
# =====================================================================
# In infrastructure/cfg.py die Struktur anpassen:

# Datei: infrastructure/cfg.py
# Vollständiges Master-Schema für die hybride IDE-Struktur

# Datei: infrastructure/cfg.py -> Ganz unten ersetzen

UI_SCHEMA = {
    "menu_structure": {
        "file": {
            "i18n_key": "menu.file",
            "items": [
                {"type": "action", "id": "menu.file.language", "command_class": "ChangeLanguageCommand"},
                {"type": "action", "id": "menu.file.ollama", "command_class": "OllamaInfoCommand"},
                {"type": "action", "id": "menu.file.validate", "command_class": "OllamaValidateCommand"},
                {"type": "action", "id": "menu.file.edit_locales", "command_class": "LanguageEditorCommand"},
                {"type": "separator"},
                {"type": "action", "id": "menu.file.reset_system", "command_class": "ResetSystemCommand"},
                {"type": "separator"},
                {"type": "action", "id": "menu.file.exit", "command_class": "ExitCommand"}
            ]
        }
    },
    "menu_order": ["file"],
    "tab_structure": [
        {
            "id": "tab.welcome",
            "i18n_key": "tabs.welcome.title",
            "label": "Willkommen",
            "layout_type": "form",
            "elements": [
                {
                    "id": "welcome_headline",
                    "type": "label",
                    "i18n_key": "welcome.headline.text",
                    "width": 400,
                    "height": 40,
                    "x": 20,
                    "y": 20
                },
                {
                    "id": "search_input_line",
                    "type": "input_line",
                    "placeholder_i18n": "welcome.search.placeholder",
                    "width": 250,
                    "height": 30,
                    "x": 20,
                    "y": 80
                },
                {
                    "id": "search_execute_button",
                    "type": "button",
                    "i18n_key": "welcome.button.search",
                    "macro_file": "macros.search_macro",
                    "macro_event": "execute_search",
                    "width": 120,
                    "height": 30,
                    "x": 280,
                    "y": 80
                }
            ]
        }
    ]
}





# Zentrale Definition aller wissenschaftlichen Rechts-nach-Links-Sprachen (RTL)
RTL_LANGUAGES = ["ar", "he", "fa", "ur", "ps"]

# =====================================================================
# SYSTEM-DESIGNER: REPTIL-ERWEITERUNG (PLUGINS/USER COMMANDS)
# =====================================================================
# Dieser Ordnername ist fest an das business-Paket gekoppelt. 
# Darf vom Benutzer/Entwickler weder umbenannt noch verschoben werden!
USER_COMMANDS_FOLDER = "commands_user"
USER_COMMANDS_PACKAGE = f"business.{USER_COMMANDS_FOLDER}"

# =====================================================================
# VISUELLE IDENTITÄT (CLIOGRAPH MARKETING BRANDING)
# =====================================================================
# ONCE-ONLY: Das Kleeblatt-Branding wird jetzt als echtes Anker-Icon geladen.
# Wir leeren den Text-Modifier, damit kein doppeltes Icon mehr entsteht!
APP_ICON_THEME = "clio-clover"
APP_ICON_TITLE_MODIFIER = ""  # Restlos geleert!

# Für spätere PNG-Dateien der Marketingabteilung vorbereitet
APP_ICON_PATH = "" 