# -*- coding: utf-8 -*-
"""Business Layer: System-Kommando zur Wiederherstellung der Werkseinstellungen"""

import os
import shutil
import json
from PyQt6.QtWidgets import QMessageBox
from business.commands.cmd_base import UICommand
import infrastructure.cfg as cfg

class ResetSystemCommand(UICommand):
    """Setzt das gesamte GUI-Framework und die Sprachdateien auf den Urzustand zurück."""

    @property
    def menu_key(self) -> str:
        return "menu.file.reset_system"

    def execute(self, services: dict):
        # LAZY IMPORT: Zirkuläre Importe und Side-Effects verhindern
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QMessageBox, QApplication

        i18n = services.get("i18n")
        ui_state = services.get("ui_state_manager")
        persistence = services.get("menu_persistence")

        # Helfer für bilinguale Sonden
        def get_text(key, fallback):
            return i18n.text(key) if i18n and hasattr(i18n, "text") else fallback

        # Hauptfenster-Referenz für korrekte Zuweisung suchen
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if widget.inherits("QMainWindow"):
                main_win = widget
                break

        # Hilfsfunktion, um Nachrichten-Boxen ohne Kleeblatt-Icon zu erzeugen
        def create_clean_msg_box(icon_type, title_text, body_text, buttons=QMessageBox.StandardButton.Ok):
            box = QMessageBox(main_win)
            box.setIcon(icon_type)
            box.setWindowTitle(title_text)
            box.setText(body_text)
            box.setStandardButtons(buttons)
            box.setWindowFlags(box.windowFlags() | Qt.WindowType.CustomizeWindowHint)
            box.setWindowFlags(box.windowFlags() & ~Qt.WindowType.WindowSystemMenuHint)
            return box

        # 1. Sicherheitsabfrage
        title = get_text("dialog.reset.title", "System zurücksetzen")
        msg = get_text("dialog.reset.text", "Möchten Sie das System wirklich auf die Werkseinstellungen zurücksetzen?\nAlle dynamischen Menüs und hinzugefügten Sprachen werden archiviert.")
        
        ask_box = create_clean_msg_box(
            QMessageBox.Icon.Question, 
            title, 
            msg, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        ask_box.setDefaultButton(QMessageBox.StandardButton.No)

        if ask_box.exec() != QMessageBox.StandardButton.Yes:
            return

        try:
            # SONDE 1: Start
            box1 = create_clean_msg_box(QMessageBox.Icon.Information, get_text("sonde.title.1", "Schritt 1/5"), get_text("sonde.msg.1", "Bereinigung gestartet..."))
            box1.exec()

            # SONDE 2: Datei-Bereinigung
            box2 = create_clean_msg_box(QMessageBox.Icon.Information, get_text("sonde.title.2", "Schritt 2/5"), get_text("sonde.msg.2", "Lösche Konfigurationsdatei (dynamic_menu.json)..."))
            box2.exec()

            # ABSOLUTE PFADSICHERUNG: Löscht die Datei direkt im json_storage-Ordner
            target_menu_path = os.path.join(os.getcwd(), "json_storage", "dynamic_menu.json")
            if os.path.exists(target_menu_path):
                try:
                    os.remove(target_menu_path)
                    print(f"[RESET] {target_menu_path} erfolgreich gelöscht.")
                except Exception as e:
                    print(f"[RESET-FEHLER] Konnte dynamic_menu.json nicht löschen: {e}")

            # Bereinigung der generierten Benutzer-Makros (cmd_tab_*.py)
            user_cmd_dir = os.path.join(os.getcwd(), "business", "commands_user")
            if os.path.exists(user_cmd_dir):
                for filename in os.listdir(user_cmd_dir):
                    if filename.startswith("cmd_tab_") and filename.endswith(".py"):
                        try:
                            os.remove(os.path.join(user_cmd_dir, filename))
                            print(f"[RESET] Benutzer-Makro gelöscht: {filename}")
                        except Exception as e:
                            print(f"[RESET] Fehler beim Löschen von {filename}: {e}")

            # SONDE 3: Sprach-Archivierung
            box3 = create_clean_msg_box(QMessageBox.Icon.Information, get_text("sonde.title.3", "Schritt 3/5"), get_text("sonde.msg.3", "Archiviere zusätzliche Sprachdateien..."))
            box3.exec()

            locales_dir = cfg.JSON_LOCALES_DIR
            backup_dir = os.path.join(cfg.JSON_STORAGE_DIR, "backup_locales")
            os.makedirs(backup_dir, exist_ok=True)

            if os.path.exists(locales_dir):
                for filename in os.listdir(locales_dir):
                    if filename.endswith(".json"):
                        # KORREKTUR: Erweiterter Schutzschild für alle Werksdateien
                        protected_files = [
                            "de.json", 
                            "en.json", 
                            "de_factory.json", 
                            "en_factory.json", 
                            "start_status.json"
                        ]
                        
                        if filename in protected_files:
                            continue

                        src_path = os.path.join(locales_dir, filename)
                        dst_path = os.path.join(backup_dir, filename)
                        try:
                            shutil.move(src_path, dst_path)
                            print(f"[RESET] Fremdsprache archiviert: {filename}")
                        except Exception as e:
                            print(f"[RESET] Fehler beim Verschieben von {filename}: {e}")

            # PRÄZISE POSITIONIERUNG: start_status.json am exakten Ort auf ("de", "en") setzen
            status_path = os.path.join(cfg.JSON_LOCALES_DIR, "start_status.json")
            try:
                default_status = {"active_languages": ["de", "en"]}
                with open(status_path, "w", encoding="utf-8") as f:
                    json.dump(default_status, f, ensure_ascii=False, indent=4)
                print("[RESET] start_status.json erfolgreich aktualisiert.")
            except Exception as e:
                print(f"[RESET] Fehler beim Schreiben der start_status.json: {e}")

            # OPTION A: Überschreibe die aktiven Sprachdateien radikal mit den sauberen Werkshüllen
            for lang in ["de", "en"]:
                factory_path = os.path.join(cfg.JSON_LOCALES_DIR, f"{lang}_factory.json")
                active_path = os.path.join(cfg.JSON_LOCALES_DIR, f"{lang}.json")
                if os.path.exists(factory_path):
                    try:
                        shutil.copy2(factory_path, active_path)
                        print(f"[RESET] {lang}.json erfolgreich aus Werkshülle wiederhergestellt.")
                    except Exception as e:
                        print(f"[RESET-FEHLER] Konnte {lang}.json nicht wiederherstellen: {e}")

            

            # SONDE 4: RAM-Reset (Vollständige Werkseinstellung inklusive Sidebars)
            box4 = create_clean_msg_box(QMessageBox.Icon.Information, get_text("sonde.title.4", "Schritt 4/5"), get_text("sonde.msg.4", "Setze Systemkonfigurationen im RAM zurück..."))
            box4.exec()

            cfg.APP_CONFIG["supported_languages"] = ["de", "en"]
            cfg.AVAILABLE_LANGUAGES = [{"name": "Deutsch", "code": "de"}, {"name": "English", "code": "en"}]

            # Vollständiges Werkseinstellungs-Schema mit allen Sidebars und dem Plus-Tab
            cfg.UI_SCHEMA = {
                "menu_structure": {
                    "file": {
                        "i18n_key": "menu.file",
                        "items": [
                            {"type": "action", "id": "menu.file.language", "command_class": "ChangeLanguageCommand"},
                            {"type": "action", "id": "menu.file.edit_locales", "command_class": "LanguageEditorCommand"},
                            {"type": "action", "id": "menu.file.ollama", "command_class": "OllamaInfoCommand"},
                            {"type": "action", "id": "menu.file.validate", "command_class": "OllamaValidateCommand"},
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
                        "elements": []
                    }
                ]
            }

            if ui_state:
                if hasattr(ui_state, "_undo_stack"): ui_state._undo_stack.clear()
                if hasattr(ui_state, "_redo_stack"): ui_state._redo_stack.clear()

            if persistence and hasattr(persistence, "save_menus"):
                payload = {
                    "menu_structure": cfg.UI_SCHEMA["menu_structure"],
                    "menu_order": cfg.UI_SCHEMA["menu_order"],
                    "tab_structure": cfg.UI_SCHEMA["tab_structure"],
                    "supported_languages": cfg.APP_CONFIG["supported_languages"],
                    "available_languages": cfg.AVAILABLE_LANGUAGES
                }
                persistence.save_menus(payload)

            # SONDE 5: UI-Neuaufbau
            box5 = create_clean_msg_box(QMessageBox.Icon.Information, get_text("sonde.title.5", "Schritt 5/5"), get_text("sonde.msg.5", "Initialisiere Benutzeroberfläche neu..."))
            box5.exec()

            # Da sich die Widgets durch setup_ui ändern, suchen wir das Fenster zur Sicherheit noch einmal
            for widget in QApplication.topLevelWidgets():
                if widget.inherits("QMainWindow"):
                    main_win = widget
                    break

            if main_win and hasattr(main_win, "setup_ui"):
                main_win.setup_ui()

            # Abschlussmeldung
            box_done = create_clean_msg_box(QMessageBox.Icon.Information, get_text("sonde.title.done", "Erfolg"), get_text("sonde.msg.done", "Das System wurde erfolgreich in den Urzustand zurückgesetzt!"))
            box_done.exec()

        except Exception as e:
            box_err = create_clean_msg_box(QMessageBox.Icon.Critical, "Fehler beim Reset", f"Absturz bei der Ausführung:\n{str(e)}")
            box_err.exec()
