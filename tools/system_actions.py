# Datei: tools/system_actions.py
import os
import shutil
from PyQt6.QtWidgets import QMessageBox
import infrastructure.cfg as cfg

class SystemMaintenance:
    """Kapselt alle destruktiven System-Operationen wie Sprach-Cleanups und Factory Resets."""
    
    @staticmethod
    def reset_languages_to_factory(main_window):
        """Löscht Dritt-Sprachen mit automatischem Backup, setzt RAM zurück und synchronisiert."""
        i18n = main_window._i18n
        
        # 1. Sicherheitsabfrage über das I18N-System (Zweisprachig!)
        antwort = QMessageBox.question(
            main_window,
            i18n.text("dialog.maintenance.title"),
            i18n.text("dialog.maintenance.prompt"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if antwort != QMessageBox.StandardButton.Yes:
            return
            
        try:
            # 2. BACKUP-SYSTEM: Ordner für Wiederherstellungsdateien vorbereiten
            backup_dir = os.path.join(cfg.JSON_STORAGE_DIR, "backup_locales")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
                
            # 3. Physisches Sichern und anschliessendes Löschen im locales-Ordner
            if os.path.exists(cfg.JSON_LOCALES_DIR):
                for filename in os.listdir(cfg.JSON_LOCALES_DIR):
                    if filename.endswith(".json"):
                        lang_code = filename.replace(".json", "")
                        if lang_code not in cfg.MASTER_LANGUAGES:
                            src_file = os.path.join(cfg.JSON_LOCALES_DIR, filename)
                            dst_file = os.path.join(backup_dir, filename)
                            
                            # Kopieren (Sichern) vor dem Löschen
                            shutil.copy2(src_file, dst_file)
                            # Physisch löschen
                            os.remove(src_file)
            
            # 4. RAM-Pools hart auf Ausgangszustand zurücksetzen
            cfg.APP_CONFIG["supported_languages"] = ["de", "en"]
            cfg.AVAILABLE_LANGUAGES = [
                {"name": "Deutsch", "code": "de"},
                {"name": "English", "code": "en"}
            ]
            
            # Fallback falls die App auf einer gelöschten Sprache stand
            if i18n._current_lang not in cfg.MASTER_LANGUAGES:
                main_window._change_language_trigger("de")
            
            # 5. JUST-IN-TIME PERSISTENZ (Überschreibt dynamic_menu.json blitzsauber)
            persistence = main_window._services.get("menu_persistence")
            if persistence and hasattr(persistence, "save_menus"):
                persistence.save_menus(cfg.UI_SCHEMA)
            
            # 6. UI-Neuaufbau erzwingen
            if hasattr(main_window, "refresh_ui_texts"):
                main_window.refresh_ui_texts()
            elif hasattr(main_window, "setup_ui"):
                main_window.setup_ui()
                
            # Erfolgsmeldung über das I18N-System ausgeben
            QMessageBox.information(
                main_window, 
                i18n.text("dialog.maintenance.title"), 
                i18n.text("dialog.maintenance.success")
            )
            
        except Exception as e:
            QMessageBox.critical(main_window, "Fehler", f"Fehler bei der Systembereinigung:\n{str(e)}")
