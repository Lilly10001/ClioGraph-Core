# Datei: infrastructure/menu_storage.py
import json
import os
import infrastructure.cfg as cfg

class MenuPersistenceManager:
    """
    Kapselt das Speichern und Laden der dynamischen Menüpunkte in einer JSON-Datei.
    Greift strikt auf die zentralen Pfad-Definitionen in der cfg.py zu.
    """
    
    def __init__(self, discover_func):
        self._discover_func = discover_func
        
        # --- ABSOLUTE TRENNUNG: KEINE HART CODIERTEN PFADBERECHNUNGEN ---
        # Wir lesen die Pfade direkt aus der zentralen Konfiguration aus
        self._json_folder = cfg.JSON_STORAGE_DIR
        self._storage_file = cfg.JSON_MENU_FILE
        
        # Robustheits-Check: Falls der Ordner physisch fehlt, wird er angelegt
        if not os.path.exists(self._json_folder):
            os.makedirs(self._json_folder)
            print(f"[PERSISTENZ] Zentraler Ordner angelegt: {self._json_folder}")

    def save_menus(self, dynamic_menu_store: dict):
        """Speichert das komplette UI_SCHEMA-Menüformat direkt und sauber ab."""
        try:
            # ERWEITERT: Jetzt wird auch die tab_structure dauerhaft gesichert!
            data_to_save = {
                "menu_structure": dynamic_menu_store.get("menu_structure", {}),
                "menu_order": dynamic_menu_store.get("menu_order", []),
                "tab_structure": dynamic_menu_store.get("tab_structure", []),
                "supported_languages": dynamic_menu_store.get("supported_languages", ["de", "en"]),
                "available_languages": dynamic_menu_store.get("available_languages", [])
            }
            
            with open(self._storage_file, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            print("✔ [PERSISTENZ] Menüstruktur, Reihenfolge und Registerkarten im UI_SCHEMA-Format gesichert.")
        except Exception as e:
            print(f"❌ [PERSISTENZ-FEHLER] Konnte Menüs nicht sichern: {e}")


    def load_menus(self) -> dict:
        """Liest die JSON-Datei aus und gibt die rohe menu_structure zurück."""
        if not os.path.exists(self._storage_file):
            # KORREKTUR: Wenn keine Datei da ist, nehmen wir das frische Kern-Schema aus der cfg.py!
            return {"menu_structure": cfg.UI_SCHEMA["menu_structure"]}
        try:
            with open(self._storage_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                if saved_data and "menu_structure" in saved_data:
                    print("📂 [PERSISTENZ] Menüstruktur erfolgreich geladen.")
                    return saved_data["menu_structure"]
        except Exception as e:
            print(f"❌ [PERSISTENZ-FEHLER] Fehler beim Laden: {e}")
        return {"menu_structure": cfg.UI_SCHEMA["menu_structure"]}
