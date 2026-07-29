# Datei: main.py
"""Bootstrapper: Zentraler Einstiegspunkt für die ClioGraph-Anwendung"""

import sys
import os
import json
from PyQt6.QtWidgets import QApplication

# Import der Infrastruktur- und Hilfsdienste
from infrastructure.i18n import TranslationService
from infrastructure.errors import ErrorHandlingService
from infrastructure.menu_storage import MenuPersistenceManager
import infrastructure.cfg as cfg

# Import der Core-Schichten (DAL & KI-Infrastruktur)
from database.db import GraphRepository
from infrastructure.llm_ml.llm import LlmExtractionService
from business.biz import BusinessCoordinator

from gui import MainWindow

# from infrastructure.languages.translater import DynamicLanguageManager
from infrastructure.languages.translator import DynamicLanguageManager

def main():
    # 1. System-Applikation initialisieren
    app = QApplication(sys.argv)

    # 2. Unabhängige Basis-Infrastruktur starten
    i18n_service = TranslationService(default_lang=cfg.APP_CONFIG["default_language"])
    error_service = ErrorHandlingService(i18n_service)

    # 3. Core-Schichten initialisieren (DAL & KI-Infrastruktur)
    db_repo = GraphRepository(db_path=cfg.DB_PATH)
    llm_service = LlmExtractionService(model_name=cfg.APP_CONFIG["default_model"])

    # 4. Central Service Locator Pool aufbauen & Persistenz laden
    persistence_manager = MenuPersistenceManager(discover_func=cfg.discover_all_commands)

    # ÜBERSPRÜGE DEN LÖSCH-MODUS UND LADE DIE PERSISTENTEN MENÜS:
    if os.path.exists(cfg.JSON_MENU_FILE):
        try:
            # Lade die gespeicherten Menüs von der Festplatte
            with open(cfg.JSON_MENU_FILE, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                
                if "menu_structure" in saved_data:
                    # Aktualisiere das globale Laufzeit-Schema mit den geladenen Daten
                    cfg.UI_SCHEMA["menu_structure"] = saved_data["menu_structure"]
                    
                    # === REPARATUR DER PERSISTENZ: Reihenfolge beim Starten mitladen ===
                    if "menu_order" in saved_data:
                        cfg.UI_SCHEMA["menu_order"] = saved_data["menu_order"]
                    else:
                        # Fallback: Falls die Liste in der JSON fehlt, aus den Keys generieren
                        cfg.UI_SCHEMA["menu_order"] = list(saved_data["menu_structure"].keys())

                    # === KERN-REPARATUR: Register/Tabs werden nun direkt beim Booten geladen! ===
                    if "tab_structure" in saved_data:
                        cfg.UI_SCHEMA["tab_structure"] = saved_data["tab_structure"]

                                        
                    # === NEU: REAKTIVIERUNG DER GESPEICHERTEN SPRACHEN ===
                    # 1. Aktivierte Sprachen zurück in den RAM-Pool holen
                    if "supported_languages" in saved_data:
                        for lang_code in saved_data["supported_languages"]:
                            if lang_code not in cfg.APP_CONFIG["supported_languages"]:
                                cfg.APP_CONFIG["supported_languages"].append(lang_code)
                    
                    # 2. Die Anzeigeliste für die GUI-Dropdowns absolut zerstörungsfrei wiederherstellen
                    if "available_languages" in saved_data:
                        for lang in saved_data["available_languages"]:
                            # Füge die Sprache NUR hinzu, wenn sie nicht bereits im System existiert
                            if not any(l["code"] == lang["code"] for l in cfg.AVAILABLE_LANGUAGES):
                                cfg.AVAILABLE_LANGUAGES.append(lang)
     
                    # === REPARATUR DES SCHÖNHEITSFEHLERS: START-STATUS GEGENPRÜFEN ===
                    start_status_pfad = os.path.join(cfg.JSON_LOCALES_DIR, "start_status.json")
                    if os.path.exists(start_status_pfad):
                        with open(start_status_pfad, "r", encoding="utf-8") as sf:
                            sd = json.load(sf)
                            if "active_languages" in sd:
                                # Bekannte ISO-Mapping-Tabelle für DH-Forschungssprachen
                                iso_namen = {
                                    "fr": "Français", "it": "Italiano", "es": "Español", 
                                    "ar": "Arabic", "he": "Hebrew", "fa": "Persian", 
                                    "la": "Latin", "el": "Greek", "nl": "Dutch"
                                }
                                for code in sd["active_languages"]:
                                    # Im RAM-Pool registrieren
                                    if code not in cfg.APP_CONFIG["supported_languages"]:
                                        cfg.APP_CONFIG["supported_languages"].append(code)
                                    # Im Dropdown-Pool registrieren
                                    if not any(l["code"] == code for l in cfg.AVAILABLE_LANGUAGES):
                                        display_name = iso_namen.get(code, code.upper())
                                        cfg.AVAILABLE_LANGUAGES.append({"name": display_name, "code": code})
                    
                    print("✔ [SYSTEM] Dynamische Menüstruktur und Sprachen erfolgreich geladen und synchronisiert.")
        except Exception as e:
            print(f"❌ [SYSTEM] Fehler beim Laden der Menüdatei: {e}")
    else:
        # Falls die Datei noch nie existierte (erster Start), erstelle das Ausgangsgerüst
        print("📢 [SYSTEM] Keine Menüdatei gefunden. Generiere Basis-Schema...")
        persistence_manager.save_menus(cfg.UI_SCHEMA)
    

    # 5. Service Locator Pool mit Objekten befüllen
    # Den Manager erschaffen
    language_manager = DynamicLanguageManager(services=None)

    # Das gesamte Services-Paket schnüren
    services = {
        "i18n": i18n_service,
        "errors": error_service,
        "biz": BusinessCoordinator(repository=db_repo, llm_service=llm_service),
        "command_finder": cfg.discover_all_commands,
        "menu_persistence": persistence_manager,
        "language_manager": language_manager  # <-- Hier legst du ihn hinein
    }
    
    # Dem Manager das fertige Paket zur Verfügung stellen
    language_manager._services = services

    # 6. Presentation Layer (GUI) aufbauen, Service-Pool und geladenes Schema injizieren
    main_window = MainWindow(services, cfg.UI_SCHEMA)

    # 7. Sprache initial setzen und Fenster auf dem Bildschirm anzeigen
    """main_window._change_language_trigger(cfg.APP_CONFIG["default_language"])"""
    main_window._change_language_trigger("de")
    main_window.show()

     # === NEU: REFRESH NACH DEM START FÜR DIE SIDEBAR-LISTEN ===
    main_window.setup_ui()

    # 8. Event-Loop der Anwendung starten
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
