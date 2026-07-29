# Datei: export_doc.py
# Generiert einen vollständigen Markdown-Snapshot der Projektstruktur und des Quellcodes.

import os
import subprocess
from datetime import datetime

# Konstante für den Projektnamen
APP_NAME = "ClioGraph"

# Ordner und Dateien, die strikt IGNORIERT werden (wichtig für Datenschutz & Performance)
IGNORE_DIRS = {
    '.venv', 'venv', '.git', '__pycache__', '.vscode', '.idea', 
    'kuzu_db', 'cliograph_db', '_Dokumentation'
}
# KORREKTUR: config.json entfernt, damit alle JSON-Dateien (auch dynamic_menu.json) eingelesen werden!
IGNORE_FILES = {'export_doc.py', '.env'} 

def get_git_commit():
    """Liest den kurzen Git-Commit-Hash des aktuellen Repositories aus."""
    try:
        commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=subprocess.DEVNULL)
        return commit.decode('utf-8').strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "no-git"

def generate_version():
    """Generiert einen kompakten Versions-String: v1-JJMMTT-HHMM"""
    timestamp = datetime.now().strftime("%y%m%d-%H%M")
    return f"v1-{timestamp}"

def get_unique_filename(base_dir, app_name, version):
    """Prüft, ob die Datei existiert, und generiert eine neue Versionsnummer, falls nötig."""
    filename = f"{app_name}_Stand_{version}.md"
    full_path = os.path.join(base_dir, filename)
    
    if not os.path.exists(full_path):
        return full_path
        
    counter = 2
    while True:
        filename = f"{app_name}_Stand_{version}_v{counter}.md"
        full_path = os.path.join(base_dir, filename)
        if not os.path.exists(full_path):
            return full_path
        counter += 1

def create_tree(dir_path, prefix=""):
    """Erzeugt einen visuellen Ordnerstruktur-Baum."""
    tree = ""
    contents = sorted([c for c in os.listdir(dir_path) if c not in IGNORE_DIRS and c not in IGNORE_FILES])
    pointers = [ "├── " ] * (len(contents) - 1) + [ "└── " ] if contents else []
    
    for pointer, name in zip(pointers, contents):
        path = os.path.join(dir_path, name)
        if os.path.isdir(path):
            tree += f"{prefix}{pointer}{name}/\n"
            extension = "│   " if pointer == "├── " else "    "
            tree += create_tree(path, prefix + extension)
        else:
            tree += f"{prefix}{pointer}{name}\n"
    return tree

def read_file_safely(file_path):
    """Liest eine Datei mit automatischem Fallback für verschiedene Kodierungen ein."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="utf-16") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()

def export_project():
    target_dir = "_Dokumentation"
    os.makedirs(target_dir, exist_ok=True)
    
    dynamic_version = generate_version()
    output_file = get_unique_filename(target_dir, APP_NAME, dynamic_version)
    
    with open(output_file, "w", encoding="utf-8") as doc:
        # Header für die Dokumentation
        doc.write(f"# Projekt-Dokumentation: {APP_NAME}\n\n")
        doc.write(f"- **Git-Basis-Version:** `{dynamic_version}`\n")
        doc.write(f"- **Dokumentations-Datei:** `{os.path.basename(output_file)}`\n")
        doc.write(f"- **Export-Zeitstempel:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
        
        # 1. Struktur ausgeben
        doc.write(f"## 1. Aktuelle Ordnerstruktur\n```text\n{APP_NAME}/\n")
        doc.write(create_tree("."))
        doc.write("```\n\n")
        
        # 2. Dateiinhalte gemäss Ordnerstruktur ausgeben
        doc.write("## 2. Quellcode- und Konfigurationsdateien\n\n")
        
        # KORREKTUR: Sortiert os.walk, damit die KI die Schichten logisch nacheinander liest
        for root, dirs, files in os.walk("."):
            dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS])
            
            for file in sorted(files):
                if file in IGNORE_FILES:
                    continue
                
                # Filter für relevante Dateitypen
                if not (file.endswith('.py') or file.endswith('.json') or file == '.gitignore'):
                    continue
                    
                rel_path = os.path.relpath(os.path.join(root, file), ".")
                doc.write(f"### File: `{rel_path}`\n\n")
                
                lang = "python" if file.endswith('.py') else "json" if file.endswith('.json') else "text"
                doc.write(f"```{lang}\n")
                
                content = read_file_safely(os.path.join(root, file))
                zeilen = content.splitlines()
                MAX_ZEILEN = 300 
                
                if len(zeilen) > MAX_ZEILEN:
                    gekuerzter_content = "\n".join(zeilen[:MAX_ZEILEN])
                    doc.write(gekuerzter_content)
                    doc.write(f"\n\n... [HINWEIS: Datei wurde hier nach {MAX_ZEILEN} Zeilen gekürzt] ...")
                else:
                    doc.write(content)
                    
                doc.write("\n```\n\n")
                
    print(f"✅ Dokumentation (perfekt für KI-Kontext) erfolgreich gesichert unter: {output_file}")

if __name__ == "__main__":
    export_project()
