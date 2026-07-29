# -*- coding: utf-8 -*-
"""
Infrastructure/Utility Layer: Kapselung des JSON-basierten Übersetzungs-Services mit robustem Code-Fallback
Erweitert um die neuen Übersetzungen für den System-Designer (Sortierung und System-Schutz).
"""

import os
import json
import infrastructure.cfg as cfg

class TranslationService:
    def __init__(self, default_lang: str = "de"):
        self._registered_widgets = {}
        self._current_lang = default_lang
        self._translations = {}  # Hier landen die geladenen JSON-Inhalte
        
        # Feste Standard-Übersetzungen als Sicherheitsnetz (Damit die GUI niemals leer bleibt!)
        self._fallback_translations = {
            "de": {
                "app.title": "ClioGraph ➖ Historische Graphen-Analyse & Graph-RAG",
                "menu.file": "Datei",
                "menu.file.language": "Sprache wechseln",
                "menu.file.exit": "Beenden",
                "mod1.title": "Wissens-Extraktion",
                # --- NEU: Übersetzungen für die Sicherheits-Knöpfe ---
                "sidebar.safety.undo": " Rückgängig",
                "sidebar.safety.redo": " Wiederholen",
                
                # --- System-Designer (Hauptmenü) ---
                "sidebar.designer.title": "⚙️ SYSTEM-DESIGNER",
                "sidebar.menu.group": "⚙️ HAUPTMENÜ",
                "sidebar.menu.add": "+ Neues Hauptmenü",
                "sidebar.menu.delete": "- Hauptmenü löschen",
                "sidebar.menu.rename": "✏️ Hauptmenü umbenennen",
                "sidebar.menu.move_left": "◀ Nach links",
                "sidebar.menu.move_right": "▶ Nach rechts",
                
                # --- System-Designer (Schaltflächen / Items) ---
                "sidebar.item.group": "📝 MENÜEINTRÄGE",
                "sidebar.item.add": "+ Neues Item",
                "sidebar.item.delete": "- Item löschen",
                "sidebar.item.rename": "✏️ Item umbenennen",
                "sidebar.item.assign": "⚡ Befehl zuordnen",
                "sidebar.item.move_up": "▲ Nach oben",
                "sidebar.item.move_down": "▼ Nach unten",
                
                # --- System-Designer (Registerkarten / Tabs) ---
                "sidebar.tab.group": "🗂️ REGISTERKARTEN",
                "sidebar.tab.add": "+ Neues Register",
                "sidebar.tab.delete": "- Register löschen",
                "sidebar.tab.rename": "✏️ Register umbenennen",
                "sidebar.tab.move_left": "◀ Links verschieben",
                "sidebar.tab.move_right": "▶ Rechts verschieben",
                
                # --- System-Designer (Schutz- und Warnmeldungen) ---
                "msg.protection.title": "System-Schutzfunktion",
                "msg.protection.core_deny": "Dieses Element gehört zum geschützten Systemkern und darf weder gelöscht, verschoben noch umbenannt werden!"
            },
            "en": {
                "app.title": "ClioGraph ➖ Historical Graph Analytics & Graph-RAG",
                "menu.file": "File",
                "menu.file.language": "Change Language",
                "menu.file.exit": "Exit",
                "mod1.title": "Knowledge Extraction",

                # --- NEU: Übersetzungen für die Sicherheits-Knöpfe ---
                "sidebar.safety.undo": " Undo",
                "sidebar.safety.redo": " Redo",   
                
                # --- System Designer (Main Menu) ---
                "sidebar.designer.title": "⚙️ SYSTEM DESIGNER",
                "sidebar.menu.group": "⚙️ MAIN MENU",
                "sidebar.menu.add": "+ New Main Menu",
                "sidebar.menu.delete": "- Delete Main Menu",
                "sidebar.menu.rename": "✏️ Rename Main Menu",
                "sidebar.menu.move_left": "◀ Move Left",
                "sidebar.menu.move_right": "▶ Move Right",
                
                # --- System Designer (Buttons / Items) ---
                "sidebar.item.group": "📝 MENU ITEMS",
                "sidebar.item.add": "+ New Item",
                "sidebar.item.delete": "- Delete Item",
                "sidebar.item.rename": "✏️ Rename Item",
                "sidebar.item.assign": "⚡ Assign Command",
                "sidebar.item.move_up": "▲ Move Up",
                "sidebar.item.move_down": "▼ Move Down",
                
                # --- System Designer (Tabs) ---
                "sidebar.tab.group": "🗂️ TABS",
                "sidebar.tab.add": "+ New Tab",
                "sidebar.tab.delete": "- Delete Tab",
                "sidebar.tab.rename": "✏️ Rename Tab",
                "sidebar.tab.move_left": "◀ Move Left",
                "sidebar.tab.move_right": "▶ Move Right",
                
                # --- System Designer (Protection Messages) ---
                "msg.protection.title": "System Protection",
                "msg.protection.core_deny": "This element belongs to the protected system core and cannot be deleted, moved, or renamed!"
            }
        }
        
        self._locales_dir = cfg.JSON_LOCALES_DIR
        self._load_all_locales()

    def _load_all_locales(self):
        """Lädt alle verfügbaren JSON-Sprachdateien dynamisch aus dem json_storage."""
        if not os.path.exists(self._locales_dir):
            os.makedirs(self._locales_dir, exist_ok=True)
            
        for lang_code in cfg.APP_CONFIG.get("supported_languages", ["de", "en"]):
            file_path = os.path.join(self._locales_dir, f"{lang_code}.json")
            
            # Starten mit den eingebauten Code-Fallbacks
            self._translations[lang_code] = dict(self._fallback_translations.get(lang_code, {}))
            
            # Wenn eine Datei auf der Festplatte existiert, überschreiben wir die Werte damit
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_data = json.load(f)
                        if file_data:
                            self._translations[lang_code].update(file_data)
                    print(f"📂 [I18N] Sprachdatei '{lang_code}.json' erfolgreich geladen und synchronisiert.")
                except Exception as e:
                    print(f"❌ [I18N-FEHLER] Konnte {lang_code}.json nicht lesen: {e}")

    def register(self, widget, widget_type: str, i18n_key: str):
        """Registriert ein GUI-Widget für den dynamischen Sprachwechsel."""
        self._registered_widgets[widget] = (widget_type, i18n_key)

    def change_language(self, lang_code: str):
        """Wechselt die Sprache global im Service und aktualisiert alle Komponenten."""
        if lang_code in cfg.APP_CONFIG.get("supported_languages", ["de", "en"]):
            self._current_lang = lang_code
            self.translate_all()

    def text(self, key: str) -> str:
        """Holt den übersetzten Text für einen technischen Schlüssel aus den JSON-Daten."""
        lang_dict = self._translations.get(self._current_lang, {})
        if key in lang_dict:
            return lang_dict[key]
            
        default_dict = self._translations.get(cfg.APP_CONFIG["default_language"], {})
        if key in default_dict:
            return default_dict[key]
            
        return key

    def translate_all(self):
        """Übersetzt alle dynamisch angemeldeten GUI-Widgets zur Laufzeit."""
        for widget, (w_type, key) in self._registered_widgets.items():
            try:
                translated_text = self.text(key)
                
                if w_type == "headline":
                    widget.setText(f"<h3>{translated_text}</h3>")
                    
                elif w_type == "placeholder":
                    # Deckt ab (laut Grafik): 'Kombinationsfeld', 'Eingabe-Zeile', 'Text-Feld', 'Text-Anzeige'
                    widget.setPlaceholderText(translated_text)
                    
                elif w_type in ["button", "label", "checkbox", "radiobutton"]:
                    # Deckt ab (laut Grafik): 'Schaltfläche', 'Bezeichnung', 'Kontrollkästchen', 'Optionsfeld'
                    widget.setText(translated_text)
                    
                elif w_type == "groupbox":
                    # Deckt ab (laut Grafik): 'Gruppenfeld' (benötigt .setTitle)
                    widget.setTitle(translated_text)
                    
                elif w_type == "welcome_html":
                    # Verhindert ein Überschreiben des Forscher-Eingabetextes und lädt reines HTML
                    widget.setHtml(translated_text)
            except Exception:
                pass

    def update_or_append_key(self, key: str, de_text: str, en_text: str):
        """Fügt zur Laufzeit einen neuen GUI-Schlüssel direkt in die physischen JSON-Dateien ein."""
        if "de" not in self._translations: self._translations["de"] = {}
        if "en" not in self._translations: self._translations["en"] = {}
        
        self._translations["de"][key] = de_text
        self._translations["en"][key] = en_text
        
        de_file = os.path.join(self._locales_dir, "de.json")
        try:
            with open(de_file, "w", encoding="utf-8") as f:
                json.dump(self._translations["de"], f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Fehler beim Schreiben in de.json: {e}")
            
        en_file = os.path.join(self._locales_dir, "en.json")
        try:
            with open(en_file, "w", encoding="utf-8") as f:
                json.dump(self._translations["en"], f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Fehler beim Schreiben in en.json: {e}")
