# Datei: business/commands/cmd_file.py
from abc import abstractmethod

from business.commands.cmd_base import UICommand
from PyQt6.QtCore import Qt
import infrastructure.cfg as cfg
import os
import json

class ProjectExportCommand(UICommand):
    """Kapselt die Fachlogik für den Export des aktuellen DH-Projekts."""
    @property
    def menu_key(self) -> str:
        return "menu.file.export"
        
    def execute(self, services: dict):
        print("[Datei-Container] Starte den Projektexport...")

class OllamaInfoCommand(UICommand):
    """Befehl zur Anzeige der lokalen Ollama-Offline-KI Hilfsinformationen."""
    
    @property
    def menu_key(self) -> str:
        return "menu.file.ollama"

    def execute(self, services: dict):
        print("🚀 [DEBUG] OllamaInfoCommand.execute wurde ERFOLGREICH aufgerufen!")
        from PyQt6.QtWidgets import QMessageBox
        
        # Ein unzerbrechlicher Informationstext direkt im Quellcode
        titel = "Ollama-Dienst (KI-Infrastruktur)"
        
        text = (
            "<h3>Lokale Offline-KI für ClioGraph</h3>"
            "Dieses System nutzt Ollama, um historische Daten vollkommen "
            "lokal und datenschutzkonform auf Ihrem Rechner zu verarbeiten.<br><br>"
            "<b>Schritte zur Einrichtung:</b><br>"
            "1. Laden Sie Ollama für Ihr Betriebssystem herunter.<br>"
            "2. Installieren und starten Sie die Anwendung im Hintergrund.<br><br>"
            "<b>Download-Link:</b><br>"
            "<a href='https://ollama.com'>https://ollama.com</a>"
        )
        
        # Die Box wird völlig frei im Vordergrund geschaltet
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(titel)
        
        # JETZT KORREKT: Holt sich das Flag sicher aus dem Qt-Kernmodul
        from PyQt6.QtCore import Qt
        msg.setTextInteractionFlags(msg.textInteractionFlags() | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()


class OllamaValidateCommand(UICommand):
    """Zentraler Sprachen-Assistent mit hierarchischem Dropdown (EU & Intl) und Hybridmodus."""
    def __init__(self, main_win=None, i18n_service=None):
        # Das =None verhindert jetzt auch hier den Absturz beim Scannen!
        super().__init__()
        
        # Falls die GUI den Service nicht übergibt, holen wir das Singleton:
        if i18n_service is None:
            from infrastructure.i18n import TranslationService
            self.i18n = TranslationService()
        else:
            self.i18n = i18n_service

    @property
    def menu_key(self) -> str:
        return "menu.file.validate"

   
    def execute(self, services: dict):
        i18n = services.get("i18n")
        lang_mgr = services.get("language_manager")
        if not i18n or not lang_mgr: return

        from PyQt6.QtWidgets import QMessageBox, QApplication, QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout, QComboBox
        from PyQt6.QtCore import QLocale
        from PyQt6.QtGui import QStandardItemModel, QIcon
        import json
        import os

        # 1. ERST DAS MAINWINDOW SUCHEN (Damit der Dialog ein stabiles Fundament hat)
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if widget.inherits("QMainWindow") or widget.__class__.__name__ == "MainWindow":
                main_win = widget
                break

        # 2. DIALOGFENSTER ERSTELLEN UND DAS MAINWINDOW ALS PARENT ÜBERGEBEN
        dialog = QDialog(main_win)
        dialog.setWindowTitle(i18n.text("dialog.assistant.title"))
        dialog.setMinimumWidth(480)

        # FIX: Das geerbte Kleeblatt-Icon für diesen Dialog entfernen
        dialog.setWindowIcon(QIcon()) 

        # HIER WIRD 'layout' DEFINIERT:
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        lbl_info = QLabel(i18n.text("dialog.assistant.info"))
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)
        layout.addWidget(QLabel(" "))

        # === UNZERBRECHLICHE EINLESEN AUS DEM START-STATUS ===
        gespeicherte_aktive_sprachen = ["de", "en"]
        start_status_pfad = os.path.join(cfg.JSON_LOCALES_DIR, "start_status.json")

        if os.path.exists(start_status_pfad):
            try:
                with open(start_status_pfad, "r", encoding="utf-8") as sf:
                    sd = json.load(sf)
                    if "active_languages" in sd:
                        gespeicherte_aktive_sprachen = sd["active_languages"]
                for code in gespeicherte_aktive_sprachen:
                    if code not in cfg.APP_CONFIG["supported_languages"]:
                        cfg.APP_CONFIG["supported_languages"].append(code)
            except Exception as e:
                print(f" Fehler beim Lesen des Start-Status: {e}")

        
        # 2. DIALOGFENSTER ERSTELLEN UND DAS MAINWINDOW ALS PARENT ÜBERGEBEN
        # GRUPPE A: Europäische Hauptsprachen (Häkchen mit Live-Existenzprüfung)
        layout.addWidget(QLabel(f"<b>{i18n.text('dialog.assistant.group.eu')}</b>"))
        eu_sprachen = {
            "English (Standard)": ("en", "English"),
            "Français (CH)": ("fr", "French"),
            "Italiano (CH)": ("it", "Italian"),
            "Español": ("es", "Spanish")
        }
                
        checkbox_mapping = {}
        for label_text, (code, name_en) in eu_sprachen.items():
            file_path = os.path.join(cfg.JSON_LOCALES_DIR, f"{code}.json")
            datei_existiert = os.path.exists(file_path)
            
            # Absolute Wahrheit aus unserer dedizierten Status-Datei
            ist_aktiv = (code in gespeicherte_aktive_sprachen)
            
            if code in cfg.MASTER_LANGUAGES:
                final_label = f"{label_text} 🟢 (Systemkern)"
            elif datei_existiert and not ist_aktiv:
                final_label = f"{label_text} 🟡 (Im Archiv vorhanden)"
            elif datei_existiert and ist_aktiv:
                final_label = f"{label_text} 🟢 (Bereits aktiv)"
            else:
                final_label = f"{label_text} ⚪ (Bereit zum Anlegen)"
            
            cb = QCheckBox(final_label)
            
            if code == "en" or ist_aktiv: 
                cb.setChecked(True)
            else:
                cb.setChecked(False)
                
            layout.addWidget(cb)
            checkbox_mapping[cb] = (code, name_en)

        layout.addWidget(QLabel(" "))

        # GRUPPE B: Systemweiter ISO-Standard für das Dropdown
        layout.addWidget(QLabel(f"<b>{i18n.text('dialog.assistant.group.intl')}</b>"))
        combo_intl = QComboBox()
        combo_intl.addItem(i18n.text("dialog.assistant.dropdown.none"), None)
        
        any_country = getattr(QLocale.Country, "AnyCountry", getattr(QLocale, "AnyCountry", None))
        if any_country is None:
            any_country = QLocale.Country(0) if hasattr(QLocale, "Country") else 0

        eu_amtssprachen = [
            "bg", "cs", "da", "et", "fi", "el", "ga", "hr", 
            "lv", "lt", "mt", "nl", "pl", "pt", "ro", "sk", "sl", "sv", "la"
        ]
        intl_wissenschaftssprachen = ["ar", "he", "fa", "hi", "zh", "ja", "ko", "ru", "tr"]

        # Festplatte scannen, um archivierte Dateien für das Dropdown zu erkennen
        vorhandene_dateien = os.listdir(cfg.JSON_LOCALES_DIR) if os.path.exists(cfg.JSON_LOCALES_DIR) else []
        archivierte_codes = [f.replace(".json", "") for f in vorhandene_dateien if f.endswith(".json")]

        all_locales = QLocale.matchingLocales(QLocale.Language.AnyLanguage, QLocale.Script.AnyScript, any_country)
        added_iso_codes = set()
        
        eu_items = []
        intl_items = []

        for loc in all_locales:
            locale_name = loc.name()
            if not locale_name: continue
                
            parts = locale_name.split("_")
            iso_code = parts[0].lower()
            
            if len(iso_code) != 2 or iso_code in added_iso_codes:
                continue
                
            native_name = QLocale.languageToString(loc.language())
            
            # === DYNAMISCHE STATUS-ERMITTLUNG FÜR DIE DROPDOWN-ELEMENTE ===
            if iso_code in cfg.MASTER_LANGUAGES:
                status_str = "🟢 Systemkern"
            elif iso_code in cfg.APP_CONFIG["supported_languages"]:
                status_str = "🟢 Bereits aktiv"
            elif iso_code in archivierte_codes:
                status_str = "🟡 Im Archiv vorhanden"
            else:
                status_str = "⚪ Bereit zum Anlegen"
            
            display_str = f"{native_name} ({iso_code})  |  {status_str}"
            data_tuple = (iso_code, native_name)
            
            if iso_code in eu_amtssprachen:
                eu_items.append((display_str, data_tuple))
                added_iso_codes.add(iso_code)
            elif iso_code in intl_wissenschaftssprachen:
                intl_items.append((display_str, data_tuple))
                added_iso_codes.add(iso_code)

        eu_items.sort(key=lambda x: x[0])
        intl_items.sort(key=lambda x: x[0])

        model = combo_intl.model()
        combo_intl.addItem("--- EU-AMTSPRACHEN ---", None)
        if isinstance(model, QStandardItemModel):
            item = model.item(combo_intl.count() - 1)
            if item:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setEnabled(False)

        for display_str, data_tuple in eu_items:
            combo_intl.addItem(display_str, data_tuple)
        
        # Sonderprüfung für Latein-Status
        la_status = "🟢 Systemkern" if "la" in cfg.MASTER_LANGUAGES else ("🟢 Bereits aktiv" if "la" in cfg.APP_CONFIG["supported_languages"] else ("🟡 Im Archiv vorhanden" if "la" in archivierte_codes else "⚪ Bereit zum Anlegen"))
        combo_intl.addItem(f"Latin / Latein (la)  |  {la_status}", ("la", "Latin"))
        combo_intl.insertSeparator(combo_intl.count())
        
        combo_intl.addItem("--- INTERNATIONALE SPRACHEN ---", None)
        if isinstance(model, QStandardItemModel):
            item = model.item(combo_intl.count() - 1)
            if item:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setEnabled(False)

        for display_str, data_tuple in intl_items:
            combo_intl.addItem(display_str, data_tuple)
            
        layout.addWidget(combo_intl)
        layout.addWidget(QLabel(" "))
        
        # 2. DIE AKTIONS-STEUERUNG (Buttons)
        btn_layout = QHBoxLayout()
        
        # Beenden (Abbruch-Weg)
        btn_cancel = QPushButton(i18n.text("dialog.assistant.btn.cancel"))
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_layout.addStretch()
        
        # Das transaktionale OK-Muster zum Bestätigen der Sprachauswahl
        btn_ok = QPushButton(i18n.text("dialog.assistant.btn.ok"))
        btn_ok.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        btn_ok.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_ok)
        
        layout.addLayout(btn_layout)

        # Wenn der Forscher das Fenster schliesst oder Beenden klickt, brechen wir ab
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._action_mode = "manual"



        # 3. VERARBEITUNG DER ENTSCHEIDUNG
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if widget.inherits("QMainWindow") or widget.__class__.__name__ == "MainWindow":
                main_win = widget
                break

        if main_win: 
            main_win.setDisabled(True)

        ausgewaehlte_sprachen_log = []
        targets_to_process = []
        languages_to_deactivate = []

        for cb, (target_code, target_name_en) in checkbox_mapping.items():
            if cb.isChecked():
                # HIER WIRD IHRE GENIALE LOGIK AUF ALLE KUGELNFARBEN ERWEITERT:
                clean_label = cb.text().split(" 🟢")[0].split(" 🟡")[0].split(" ⚪")[0].strip()
                targets_to_process.append((target_code, target_name_en, clean_label))
            else:
                if target_code not in ["de", "en"]:
                    languages_to_deactivate.append(target_code)



        selected_intl = combo_intl.currentData()
        if selected_intl is not None:
            intl_code, intl_name_en = selected_intl
            # Trennt sauber am Balken auf und liefert den reinen Namen, z.B. "Arabic (ar)"
            clean_intl_name = combo_intl.currentText().split("  |")[0].strip()
            targets_to_process.append((intl_code, intl_name_en, clean_intl_name))

        # --- A) ARCHIVIEREN ---
        for lang_code in languages_to_deactivate:
            if lang_code in cfg.APP_CONFIG["supported_languages"]:
                cfg.APP_CONFIG["supported_languages"].remove(lang_code)
            cfg.AVAILABLE_LANGUAGES = [l for l in cfg.AVAILABLE_LANGUAGES if l["code"] != lang_code]
            ausgewaehlte_sprachen_log.append(f"{lang_code.upper()} (Archiviert)")

        # --- B) LIVE-AKTIVIEREN ---
        for target_code, target_name_en, display_name in targets_to_process:
            if target_code not in cfg.APP_CONFIG["supported_languages"]:
                cfg.APP_CONFIG["supported_languages"].append(target_code)
                
            if not any(l["code"] == target_code for l in cfg.AVAILABLE_LANGUAGES):
                cfg.AVAILABLE_LANGUAGES.append({"name": display_name, "code": target_code})
                
            ausgewaehlte_sprachen_log.append(target_name_en)

        # Nach der Verarbeitung: Oberfläche freigeben und permanent speichern
        if main_win:
            main_win.setEnabled(True)
            if hasattr(main_win, "statusBar") and main_win.statusBar():
                main_win.statusBar().clearMessage()
            
            # === DIE UNZERBRECHLICHE REISZLEINE: DEDIZIERTER START-STATUS PFADSICHER SPEICHERN ===
            try:
                start_status_pfad = os.path.join(cfg.JSON_LOCALES_DIR, "start_status.json")
                status_daten = {
                    "active_languages": cfg.APP_CONFIG["supported_languages"]
                }
                with open(start_status_pfad, "w", encoding="utf-8") as sf:
                    json.dump(status_daten, sf, indent=4, ensure_ascii=False)
                print(f"💾 [PERSISTENZ] Start-Zustand erfolgreich in start_status.json gesichert.")
            except Exception as e:
                print(f"❌ Fehler beim Schreiben des Start-Status: {e}")
            
            # UI im Hauptfenster neu aufbauen
            if hasattr(main_win, "refresh_ui_texts"): 
                main_win.refresh_ui_texts()

        # Erfolgsmeldung anzeigen
        log_str = ", ".join(ausgewaehlte_sprachen_log)
        success_msg = i18n.text("dialog.assistant.msg.success").format(log=log_str)
        QMessageBox.information(None, i18n.text("dialog.assistant.title"), success_msg)


class LanguageEditorCommand(UICommand):
    """Interaktiver In-App Sprachdateien-Editor mit gesperrten Original-Referenzspalten."""
    
    def __init__(self, main_win=None):
        # Diese Methode fügst du neu ein, damit der Scanner fehlerfrei startet!
        super().__init__()
        
    @property
    def menu_key(self) -> str:
        return "menu.file.edit_locales"

    def execute(self, services: dict):
        i18n = services.get("i18n")
        lang_mgr = services.get("language_manager")
        if not i18n or not lang_mgr: return

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
        from PyQt6.QtCore import Qt
        import os
        import json

        # 1. ERST DAS MAINWINDOW SUCHEN (Für ein stabile Fundament)
        main_win = None
        from PyQt6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if widget.inherits("QMainWindow") or widget.__class__.__name__ == "MainWindow":
                main_win = widget
                break

        # 2. INTERAKTIVES DIALOGFENSTER DESIGNEN MIT PARENT-ÜBERGABE
        dialog = QDialog(main_win)
        dialog.setWindowTitle(i18n.text("dialog.editor.title"))
        # KORREKTUR: Ermöglicht das Minimieren (_) des Fensters während des KI-Laufs!
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint)
        dialog.setMinimumSize(850, 550)

        layout = QVBoxLayout()
        dialog.setLayout(layout)
        layout.addWidget(QLabel(f"<b>{i18n.text('dialog.editor.label.select')}</b>"))

        # OBERE STATUS-STEUERUNG (Horizontal aufgereiht)
        status_layout = QHBoxLayout()
        combo_lang = QComboBox()
        status_layout.addWidget(combo_lang, 2)

        lbl_status_icon = QLabel("🟢 Aktiv")
        lbl_status_icon.setStyleSheet("font-weight: bold; margin-left: 10px; margin-right: 10px;")
        status_layout.addWidget(lbl_status_icon, 1)

        btn_toggle_status = QPushButton("Status umschalten")
        status_layout.addWidget(btn_toggle_status, 2)
        layout.addLayout(status_layout)
        layout.addWidget(QLabel(" "))

        # Tabelle initialisieren (4 Spalten: Schlüssel, DE-Ref, EN-Ref, Target-Editierbar)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            i18n.text("dialog.editor.col.key"),
            i18n.text("dialog.editor.col.de"),
            i18n.text("dialog.editor.col.en"),
            i18n.text("dialog.editor.col.target")
        ])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)
        layout.addWidget(QLabel(" "))

        # Vorhandene Sprachdateien aus dem Verzeichnis scannen
        all_files = os.listdir(cfg.JSON_LOCALES_DIR)
        available_codes = [f.replace(".json", "") for f in all_files if f.endswith(".json") and f != "start_status.json"]
        
        # Sicherstellen, dass die Master-Sprachen de und en immer auswählbar sind
        for master in cfg.MASTER_LANGUAGES:
            if master not in available_codes:
                available_codes.append(master)

        # === REPARATUR: FRISCH IM ASSISTENTEN FREIGESCHALTETE SPRACHEN EBENFALLS ANZEIGEN ===
        for active_code in cfg.APP_CONFIG.get("supported_languages", []):
            if active_code not in available_codes:
                available_codes.append(active_code)
                
        for code in sorted(available_codes):
            combo_lang.addItem(f"📦 Locale-Package: {code.upper()} ({code})", code)
 

        de_master = i18n._translations.get("de", {})
        en_master = i18n._translations.get("en", {})

        def update_status_ui():
            """Aktualisiert die Status-Label und Buttons basierend auf der gewählten Sprache."""
            target_code = combo_lang.currentData()
            if not target_code: return
            
            if target_code in cfg.MASTER_LANGUAGES:
                lbl_status_icon.setText("🟢 Systemkern")
                btn_toggle_status.setText("Geschützt")
                btn_toggle_status.setEnabled(False)
                btn_toggle_status.setStyleSheet("")
            elif target_code in cfg.APP_CONFIG["supported_languages"]:
                lbl_status_icon.setText("🟢 Aktiviert")
                btn_toggle_status.setText("Deaktivieren (Archivieren)")
                btn_toggle_status.setEnabled(True)
                btn_toggle_status.setStyleSheet("background-color: #ffc107; color: black; border: 1px solid #ced4da; padding: 4px;")
            else:
                lbl_status_icon.setText("🟡 Archiviert (Inaktiv)")
                btn_toggle_status.setText("Aktivieren")
                btn_toggle_status.setEnabled(True)
                btn_toggle_status.setStyleSheet("background-color: #28a745; color: white; border: 1px solid #ced4da; padding: 4px;")

        def handle_toggle_status_click():
            """Schaltet den Aktivierungsstatus der selektierten Sprache live um."""
            from PyQt6.QtWidgets import QApplication 
            
            target_code = combo_lang.currentData()
            if not target_code or target_code in cfg.MASTER_LANGUAGES: return
            
            if target_code in cfg.APP_CONFIG["supported_languages"]:
                cfg.APP_CONFIG["supported_languages"].remove(target_code)
                cfg.AVAILABLE_LANGUAGES = [l for l in cfg.AVAILABLE_LANGUAGES if l["code"] != target_code]
                if hasattr(i18n, "current_language") and i18n.current_language == target_code:
                    i18n.current_language = cfg.APP_CONFIG["default_language"]
            else:
                if target_code not in cfg.APP_CONFIG["supported_languages"]:
                    cfg.APP_CONFIG["supported_languages"].append(target_code)
                
                lang_display = target_code.upper()
                target_file = os.path.join(cfg.JSON_LOCALES_DIR, f"{target_code}.json")
                if os.path.exists(target_file):
                    try:
                        with open(target_file, "r", encoding="utf-8") as f:
                            meta_data = json.load(f)
                            lang_display = meta_data.get("meta", {}).get("language", target_code.upper())
                    except: pass
                if not any(l["code"] == target_code for l in cfg.AVAILABLE_LANGUAGES):
                    cfg.AVAILABLE_LANGUAGES.append({"name": lang_display, "code": target_code})
            
            if main_win:
                persistence = main_win._services.get("menu_persistence")
                if persistence and hasattr(persistence, "save_menus"):
                    speicher_daten = {
                        "menu_structure": cfg.UI_SCHEMA.get("menu_structure", {}),
                        "supported_languages": cfg.APP_CONFIG["supported_languages"],
                        "available_languages": cfg.AVAILABLE_LANGUAGES
                    }
                    persistence.save_menus(speicher_daten)
                    print(f"  [EDITOR] Aktivierungs-Status für '{target_code}' permanent gesichert.")
                    
                    try:
                        start_status_pfad = os.path.join(cfg.JSON_LOCALES_DIR, "start_status.json")
                        status_daten = {"active_languages": cfg.APP_CONFIG["supported_languages"]}
                        with open(start_status_pfad, "w", encoding="utf-8") as sf:
                            json.dump(status_daten, sf, indent=4, ensure_ascii=False)
                        print(f"  [EDITOR -> PERSISTENZ] start_status.json erfolgreich synchronisiert.")
                    except Exception as e:
                        print(f"  [EDITOR -> FEHLER] Konnte start_status.json nicht schreiben: {e}")
            
            if hasattr(main_win, "refresh_ui_texts"): 
                main_win.refresh_ui_texts()
            update_status_ui()

        btn_toggle_status.clicked.connect(handle_toggle_status_click)

        def load_selected_locale_into_table():
            """Lädt die gewählte JSON-Datei und befüllt die editierbaren Zeilen."""
            update_status_ui()
            target_code = combo_lang.currentData()
            if not target_code: return
            
            target_translations = i18n._translations.get(target_code, {})
            if not target_translations:
                target_file = os.path.join(cfg.JSON_LOCALES_DIR, f"{target_code}.json")
                if os.path.exists(target_file):
                    try:
                        with open(target_file, "r", encoding="utf-8") as f:
                            package_data = json.load(f)
                            target_translations = package_data.get("translations", package_data)
                    except Exception:
                        target_translations = {}

            table.setRowCount(0)
            table.setRowCount(len(de_master))
            for row, (key, de_val) in enumerate(de_master.items()):
                item_key = QTableWidgetItem(key)
                item_key.setFlags(item_key.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, 0, item_key)
                
                item_de = QTableWidgetItem(de_val)
                item_de.setFlags(item_de.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, 1, item_de)
                
                en_val = en_master.get(key, "[Missing in EN]")
                item_en = QTableWidgetItem(en_val)
                item_en.setFlags(item_en.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, 2, item_en)
                
                target_val = target_translations.get(key, "")
                item_target = QTableWidgetItem(target_val)
                table.setItem(row, 3, item_target)

        combo_lang.currentIndexChanged.connect(load_selected_locale_into_table)
        load_selected_locale_into_table()

        # 2. SPEICHER-STEUERUNG UND NEUER KI-BUTTON
        btn_layout = QHBoxLayout()
        btn_close = QPushButton(i18n.text("dialog.assistant.btn.ok"))
        btn_close.setStyleSheet("font-weight: bold; min-width: 80px;")
        
        btn_editor_ki = QPushButton("🟢 KI-Übersetzungsvorschlag")
        btn_save = QPushButton(i18n.text("dialog.editor.btn.save"))

        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(btn_editor_ki)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        self._abort_ki_process = False

        def run_ai_translation_for_table():
            """Fragt Ollama live ab, zeigt den Fortschritt und erlaubt jederzeit den Abbruch."""
            from PyQt6.QtWidgets import QApplication, QMessageBox
            target_code = combo_lang.currentData()
            if not target_code: return
            
            if not lang_mgr.check_ollama_status():
                QMessageBox.warning(dialog, i18n.text("dialog.ollama.title"), i18n.text("dialog.ollama.error.text"))
                return
            
            has_statusbar = main_win and hasattr(main_win, "statusBar") and main_win.statusBar() is not None
            
            iso_mapping = {
                "it": "Italian", "es": "Spanish", "fr": "French", "en": "English", "de": "German",
                "ar": "Arabic", "he": "Hebrew", "fa": "Persian", "tr": "Turkish", "ru": "Russian", 
                "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "hi": "Hindi", "la": "Latin", 
                "el": "Greek", "nl": "Dutch"
            }
            target_lang_name = iso_mapping.get(target_code, "Italian")
            
            QMessageBox.information(
                dialog, 
                "KI-Generierung startet", 
                f"<b>Ollama übersetzt jetzt live nach: {target_lang_name}</b><br><br>"
                "Sie können den Fortschritt live mitverfolgen.<br><br>"
                "<b>Abbruch-Möglichkeit:</b> Wenn es Ihnen zu lange dauert, klicken Sie während des Laufs "
                "einfach unten links auf den Button <i>'🛑 KI-Lauf abbrechen'</i>."
            )
            
            self._abort_ki_process = False
            btn_close.setText("🛑 KI-Lauf abbrechen")
            btn_close.clicked.disconnect()
            
            def trigger_abort():
                self._abort_ki_process = True
                btn_close.setText("Breche ab nach Zeile...")
                btn_close.setEnabled(False)
                
            btn_close.clicked.connect(trigger_abort)
            btn_editor_ki.setEnabled(False)
            btn_save.setEnabled(False)

            for row in range(table.rowCount()):
                if self._abort_ki_process:
                    break
                    
                key_item = table.item(row, 0)
                de_item = table.item(row, 1)
                target_item = table.item(row, 3)
                
                if key_item and de_item and target_item:
                    current_text = target_item.text().strip()
                    if not current_text or "[Bitte manuell übersetzen]" in current_text or "Test" == current_text:
                        de_text = de_item.text()
                        target_item.setText(f"[Ollama übersetzt nach {target_lang_name}...]")
                        table.scrollToItem(target_item)
                        QApplication.processEvents()
                        
                        try:
                            ki_uebersetzung = lang_mgr.suggest_translation(de_text, target_lang_name)
                            if ki_uebersetzung:
                                target_item.setText(str(ki_uebersetzung).strip())
                            else:
                                target_item.setText(f"[Fehler] {de_text}")
                                
                            if has_statusbar:
                                main_win.statusBar().showMessage(f"🤖 KI-Fortschritt: Zeile {row + 1} von {table.rowCount()} erledigt.")
                            QApplication.processEvents()
                        except Exception:
                            target_item.setText(f"[Timeout] {de_text}")
                            QApplication.processEvents()
                            continue

            if has_statusbar: 
                main_win.statusBar().clearMessage()
                
            btn_close.setEnabled(True)
            btn_close.setText(i18n.text("dialog.assistant.btn.cancel"))
            btn_close.clicked.disconnect()
            btn_close.clicked.connect(dialog.reject)
            btn_editor_ki.setEnabled(True)
            btn_save.setEnabled(True)
            
            if self._abort_ki_process:
                QMessageBox.warning(dialog, "KI-Prozess abgebrochen", "⚠️ Der Übersetzungsprozess wurde angehalten. Bereits geladene Begriffe wurden behalten.")
            else:
                QMessageBox.information(dialog, "KI-Prozess beendet", "Lokale KI hat die Übersetzungsvorschläge erfolgreich eingetragen!")

        def save_table_changes():
            """Liest die Tabelle aus, speichert die JSON mit Metadaten-Struktur und aktualisiert die App."""
            target_code = combo_lang.currentData()
            if not target_code: return
            
            updated_translations = {}
            for row in range(table.rowCount()):
                key_item = table.item(row, 0)
                target_item = table.item(row, 3)
                if key_item and target_item:
                    key = key_item.text()
                    value = target_item.text().strip()
                    if value:
                        updated_translations[key] = value
                        
            target_file = os.path.join(cfg.JSON_LOCALES_DIR, f"{target_code}.json")
            iso_mapping = {"it": "Italiano", "es": "Español", "fr": "Français", "en": "English", "de": "Deutsch"}
            lang_display_name = iso_mapping.get(target_code, target_code.upper())
            
            full_json_structure = {
                "meta": {
                    "language": lang_display_name,
                    "code": target_code
                },
                "translations": updated_translations
            }
            
            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    json.dump(full_json_structure, f, indent=4, ensure_ascii=False)
                    
                i18n._translations[target_code] = updated_translations
                
                if main_win and hasattr(main_win, "refresh_ui_texts"):
                    main_win.refresh_ui_texts()
                    
                persistence = main_win._services.get("menu_persistence")
                if persistence and hasattr(persistence, "save_menus"):
                    persistence.save_menus(cfg.UI_SCHEMA)
                    
                QMessageBox.information(dialog, i18n.text("dialog.editor.title"), i18n.text("dialog.editor.msg.success"))
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(dialog, "Fehler", f"Konnte Sprachdatei nicht speichern:\n{str(e)}")

        btn_editor_ki.clicked.connect(run_ai_translation_for_table)
        btn_save.clicked.connect(save_table_changes)
        btn_close.clicked.connect(dialog.reject) # <-- HIER NEU EINFÜGEN!

        dialog.exec()


class SystemRefreshCommand(UICommand):
    """Befehl zum Zurücksetzen der Sprachen. Später erweiterbar zum Factory Reset."""
    @property
    def menu_key(self) -> str:
        return "menu.file.refresh"
        
    def execute(self, services: dict):
        # Wir holen uns das aktive Hauptfenster über QApplication
        from PyQt6.QtWidgets import QApplication
        from tools.system_actions import SystemMaintenance # Importiert dein neues Tool-Modul!
        
        main_win = None
        for widget in QApplication.topLevelWidgets():
            if widget.inherits("QMainWindow") or widget.__class__.__name__ == "MainWindow":
                main_win = widget
                break
                
        if main_win:
            # Ruft die gekapselte Logik im Tool-Modul auf
            SystemMaintenance.reset_languages_to_factory(main_win)
