# -*- coding: utf-8 -*-
import json
import os
import sys

# ONCE-ONLY: Hauptverzeichnis dynamisch ermitteln und im Suchpfad registrieren
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import infrastructure.cfg as cfg
# NEU: Das dauerhafte, eigenständige Rettungs-Werkzeug importieren
from tools.json_syntax_fixer import repair_json_syntax

def clean_sort_and_generate_pdf():
    """
    Sucht de.json und en.json, reinigt sie von Altlasten und 
    erzwingt eine 100%ige strukturelle Kongruenz (gleiche Keys) in beiden Dateien.
    """
    # ONCE-ONLY: Flickt eventuell vergessene Kommas vor dem Einlesen vollautomatisch zusammen!
    repair_json_syntax()
    
    print("\nStarte ClioGraph Lokalisierungs-Utility mit Synchronisations-Spiegel...")
    
    project_base = getattr(cfg, "PROJECT_ROOT", PROJECT_ROOT)
    found_locales = {}
    
    # RADAR-SCAN: Findet deine Dateien sicher in json_storage/locales/
    for root, dirs, files in os.walk(project_base):
        if ".venv" in root or ".git" in root or "__pycache__" in root:
            continue
        if "de.json" in files:
            found_locales["de"] = os.path.join(root, "de.json")
        if "en.json" in files:
            found_locales["en"] = os.path.join(root, "en.json")

    if "de" not in found_locales or "en" not in found_locales:
        print("❌ Fehler: Es müssen sowohl de.json als auch en.json im Projekt vorhanden sein!")
        return

    # Framework-Core-Defaults für die neuen Dialog-Texte (inkl. Limit-Warnfenster)
    defaults_de = {
        "dialog.item.rename.de_prompt": "Neuen DEUTSCHEN Namen eingeben:",
        "dialog.item.rename.en_prompt": "Enter new ENGLISH name:",
        "dialog.item.select_label": "Menüeintrag wählen:",
        "dialog.menu.limit_reached": "Die maximale Anzahl von {0} Hauptmenüs wurde erreicht!",
        "dialog.menu.select_label": "Hauptmenü wählen:",
        "dialog.tab.select_label": "Registerkarte wählen:"
    }

    defaults_en = {
        "dialog.item.rename.de_prompt": "Neuen DEUTSCHEN Namen eingeben:",
        "dialog.item.rename.en_prompt": "Enter new ENGLISH name:",
        "dialog.item.select_label": "Select Menu Item:",
        "dialog.menu.limit_reached": "The maximum number of {0} main menus has been reached!",
        "dialog.menu.select_label": "Select Main Menu:",
        "dialog.tab.select_label": "Select Tab:"
    }
    
    try:
        # 1. Beide Dateien einlesen
        with open(found_locales["de"], "r", encoding="utf-8") as f:
            de_data = json.load(f)
        with open(found_locales["en"], "r", encoding="utf-8") as f:
            en_data = json.load(f)
            
        # 2. Altlasten aus beiden Datensätzen entfernen
        for data_dict in [de_data, en_data]:
            keys_to_remove = [k for k in data_dict.keys() if k.startswith("menu.test") or "test_deutsch" in k]
            for k in keys_to_remove:
                del data_dict[k]

        # 3. Core-Designer-Defaults injizieren falls abwesend
        for k, val in defaults_de.items():
            if k not in de_data: de_data[k] = val
        for k, val in defaults_en.items():
            if k not in en_data: en_data[k] = val

        # 4. KONGRAUENZ-SCHLEIFE: en.json exakt an de.json angleichen
        # Jeder Key aus de.json MUSS auch in en.json existieren
        for de_key, de_val in de_data.items():
            if de_key not in en_data:
                # Falls der Key in en.json fehlt, nutzen wir den vordefinierten Default
                # oder spiegeln als Sicherheitsnetz erst mal den deutschen Inhalt
                en_data[de_key] = defaults_en.get(de_key, de_val)

        # Umgekehrt: Wenn in en.json etwas ist, das in de.json fehlt, bereinigen wir es ebenfalls
        en_keys_current = list(en_data.keys())
        for en_key in en_keys_current:
            if en_key not in de_data:
                del en_data[en_key]

        # 5. Beide Datensätze alphabetisch sortieren
        de_sorted = {k: de_data[k] for k in sorted(de_data.keys())}
        en_sorted = {k: en_data[k] for k in sorted(en_data.keys())}

        # 6. Synchronisiert auf die Festplatte schreiben
        with open(found_locales["de"], "w", encoding="utf-8") as f:
            json.dump(de_sorted, f, ensure_ascii=False, indent=4)
        with open(found_locales["en"], "w", encoding="utf-8") as f:
            json.dump(en_sorted, f, ensure_ascii=False, indent=4)

        print(f"🎉 KONGRLUENZ ERREICHT! Beide Dateien haben jetzt exakt {len(de_sorted)} identische Keys.")
        print(f"   -> de.json aktualisiert ({found_locales['de']})")
        print(f"   -> en.json aktualisiert ({found_locales['en']})")

        # Protokoll-Text für die Review-Datei schreiben
        pdf_lines = ["=== CLIOGRAPH KONGRLUENZ-EXPORT ===", f"Gesamtanzahl synchronisierter Keys: {len(de_sorted)}", ""]
        pdf_lines.append("--- SPRACHDATEI: DE.JSON ---")
        for k, v in de_sorted.items(): pdf_lines.append(f'  "{k}": "{v}"')
        pdf_lines.append("\n--- SPRACHDATEI: EN.JSON ---")
        for k, v in en_sorted.items(): pdf_lines.append(f'  "{k}": "{v}"')
        
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(tools_dir, "clioGraph_locales_review.txt"), "w", encoding="utf-8") as text_file:
            text_file.write("\n".join(pdf_lines))

    except Exception as e:
        print(f"❌ Fehler bei der Spiegelung: {e}")

if __name__ == "__main__":
    clean_sort_and_generate_pdf()
