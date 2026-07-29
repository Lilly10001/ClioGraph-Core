# -*- coding: utf-8 -*-
"""
Utility-Tool für ClioGraph: Automatischer JSON-Syntax-Reparierer.
Sucht nach fehlenden Trennungskommas am Zeilenende und korrigiert diese.
"""
import os
import sys

# Hauptverzeichnis ermitteln und im Suchpfad registrieren
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import infrastructure.cfg as cfg

def repair_json_syntax():
    print("=== CLIOGRAPH JSON SYNTAX FIXER ===")
    project_base = getattr(cfg, "PROJECT_ROOT", PROJECT_ROOT)
    
    # Pfade ermitteln basierend auf deiner Speicherstruktur
    locales_folder = os.path.join(project_base, "json_storage", "locales")
    locales = {
        "de": os.path.join(locales_folder, "de.json"),
        "en": os.path.join(locales_folder, "en.json")
    }
    
    for lang, file_path in locales.items():
        if not os.path.exists(file_path):
            print(f"ℹ️ Datei nicht gefunden (wird übersprungen): {file_path}")
            continue
            
        print(f"Analysiere {lang}.json auf Syntaxfehler...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        fixed_lines = []
        corrections_count = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Prüfen, ob es eine normale Key-Value-Zeile ist, die auf ein Anführungszeichen endet
            # aber kein Komma hat und nicht die schließende Klammer oder das Ende der Datei ist
            if (
                stripped.startswith('"') 
                and stripped.endswith('"') 
                and not stripped.endswith(",")
            ):
                # Sicherheitscheck: Wenn die NÄCHSTE Zeile eine schließende Klammer ist, darf KEIN Komma hin
                next_is_end = False
                if i + 1 < len(lines):
                    next_stripped = lines[i+1].strip()
                    if next_stripped.startswith("}") or next_stripped.startswith("]"):
                        next_is_end = True
                
                if not next_is_end:
                    # Komma anfügen (unter Beibehaltung der Zeilenumbrüche)
                    if line.endswith("\r\n"):
                        line = line.replace('"\r\n', '",\r\n')
                    elif line.endswith("\n"):
                        line = line.replace('"\n', '",\n')
                    else:
                        line += ","
                    corrections_count += 1
                    print(f"  ➔ [Zeile {i+1}] Fehlendes Trennungskomma automatisch repariert.")
                    
            fixed_lines.append(line)
            
        if corrections_count > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(fixed_lines)
            print(f"✅ {lang}.json erfolgreich mit {corrections_count} Korrektur(en) gesichert.")
        else:
            print(f"  ➔ Keine Syntaxfehler in {lang}.json gefunden.")

if __name__ == "__main__":
    repair_json_syntax()
