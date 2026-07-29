# -*- coding: utf-8 -*-
"""Presentation Layer: Adressatengerechte Entwickler-IDE (Formularsteuerung & Code-Templates)"""

import os
import uuid
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QInputDialog, QMessageBox, QFrame
from PyQt6.QtCore import Qt
import infrastructure.cfg as cfg

class IDEDesigner:
    """Isoliertes Steuerungspanel für Entwickler-Werkzeuge (Kapselung)."""
    
    @staticmethod
    def inject_ide_sidebar_at(main_window, container_widget):
        """Erzeugt das visuelle Layout innerhalb der Sidebar (Koffer-Modus)."""
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        container_widget.setLayout(panel_layout)
        
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget { border: none; background: transparent; }
            QLabel.group_title { 
                font-weight: normal; 
                text-transform: uppercase; 
                color: #2b2b2b; 
                font-size: 11px; 
                letter-spacing: 0.5px;
                margin-top: 14px; 
                margin-bottom: 4px; 
            }
            QPushButton { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 7px; text-align: left; font-size: 12px; }
            QPushButton:hover { background-color: #e9ecef; }
            QComboBox { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 5px; font-size: 12px; }
            QLineEdit { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 7px; font-size: 12px; }
        """)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(12, 5, 12, 12)
        content_layout.setSpacing(6)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_container.setLayout(content_layout)
        
        def create_separator():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("color: #ced4da; margin-top: 6px; margin-bottom: 6px;")
            return line
            
        i18n = main_window._services["i18n"]
        
        # =====================================================================
        # SEKTION 0: SAFETY ZONE (Undo / Redo ganz oben in der IDE-Sidebar)
        # =====================================================================
        lbl_safety = QLabel("SICHERHEITS-VERLAUF (IDE)")
        lbl_safety.setStyleSheet("font-weight: bold; color: #1a73e8; font-size: 10px; margin-top: 5px;")
        content_layout.addWidget(lbl_safety)

        safety_layout = QHBoxLayout()
        
        # Initialisiere den Text sofort JIT (Just-in-Time) mit sicherem Fallback
        btn_undo = QPushButton(i18n.text("sidebar.safety.undo") or "Rückgängig")
        btn_redo = QPushButton(i18n.text("sidebar.safety.redo") or "Wiederholen")

        # Registrierung für zukünftige Live-Sprachwechsel (de <-> en)
        i18n.register(btn_undo, "button", "sidebar.safety.undo")
        i18n.register(btn_redo, "button", "sidebar.safety.redo")


        # Statische Trigger-Brücke zum synchronisierten UIStateManager im RAM
        from gui.designer import MenuDesigner
        btn_undo.clicked.connect(lambda: MenuDesigner._trigger_undo(main_window))
        btn_redo.clicked.connect(lambda: MenuDesigner._trigger_redo(main_window))

        safety_layout.addWidget(btn_undo)
        safety_layout.addWidget(btn_redo)
        content_layout.addLayout(safety_layout)
        content_layout.addWidget(create_separator())
        
        # =====================================================================
        # BEREICH 1: MENÜBEFEHLE ZUORDNEN
        # =====================================================================
        lbl_cmd = QLabel(i18n.text("ide.group.menu_commands") or "📂 Menübefehle zuordnen")
        lbl_cmd.setProperty("class", "group_title")
        content_layout.addWidget(lbl_cmd)
        
        btn_assign = QPushButton(i18n.text("sidebar.item.assign_btn") or "Befehl zuordnen...")
        btn_assign.clicked.connect(lambda: IDEDesigner._live_assign_macro_to_menu(main_window))
        content_layout.addWidget(btn_assign)
        
        content_layout.addWidget(create_separator())
        
        # =====================================================================
        # BEREICH 2: REGISTER-STEUERELEMENTE
        # =====================================================================
        lbl_vba = QLabel("🛠️ Formular-Steuerelemente")
        lbl_vba.setProperty("class", "group_title")
        content_layout.addWidget(lbl_vba)
        
        combo_type = QComboBox()
        combo_type.addItem("Schaltfläche (VBA-Button)", "button")
        combo_type.addItem("Kombinationsfeld (Dropdown)", "combobox")
        combo_type.addItem("Kontrollkästchen (Checkbox)", "checkbox")
        combo_type.addItem("Optionsfeld (Radio Button)", "radiobutton")
        combo_type.addItem("Gruppenfeld (Group Box)", "groupbox")
        combo_type.addItem("Bezeichnung (Label)", "label")
        combo_type.addItem("Eingabe-Zeile (einzeilig)", "input_line")
        combo_type.addItem("Text-Feld (mehrzeilig)", "input_text")
        combo_type.addItem("Text-Anzeige (Viewer)", "text_viewer")
        content_layout.addWidget(combo_type)
        
        btn_insert = QPushButton(i18n.text("ide.btn.insert_widget") or "Baustein auf Tab platzieren")
        btn_insert.clicked.connect(lambda: IDEDesigner._live_insert_widget(main_window, combo_type.currentData()))
        content_layout.addWidget(btn_insert)
        
        move_layout = QHBoxLayout()
        move_layout.setSpacing(4)
        btn_move_up = QPushButton("🔼 Nach oben")
        btn_move_down = QPushButton("🔽 Nach unten")
        btn_move_up.setStyleSheet("font-size: 11px; padding: 5px; text-align: center;")
        btn_move_down.setStyleSheet("font-size: 11px; padding: 5px; text-align: center;")
        
        btn_move_up.clicked.connect(lambda: IDEDesigner._live_move_element(main_window, -1))
        btn_move_down.clicked.connect(lambda: IDEDesigner._live_move_element(main_window, 1))
        
        move_layout.addWidget(btn_move_up)
        move_layout.addWidget(btn_move_down)
        content_layout.addLayout(move_layout)
        
        content_layout.addWidget(create_separator())
        
        # =====================================================================
        # BEREICH 3: GENAI FORMULAR DESIGNER
        # =====================================================================
        lbl_ai = QLabel("🤖 GenAI Formular Designer")
        lbl_ai.setProperty("class", "group_title")
        content_layout.addWidget(lbl_ai)
        
        prompt_input = QLineEdit()
        prompt_input.setPlaceholderText(i18n.text("ide.placeholder.prompt") or "Formular per Prompt beschreiben...")
        content_layout.addWidget(prompt_input)
        
        btn_generate = QPushButton(i18n.text("ide.btn.generate") or "Formular generieren")
        btn_generate.clicked.connect(lambda: IDEDesigner._live_genai_build(main_window, prompt_input.text()))
        content_layout.addWidget(btn_generate)
        
        panel_layout.addWidget(content_container)
        content_layout.addStretch()

    
    @staticmethod
    def _live_assign_macro_to_menu(main_window):
        """
        Verknüpft dynamisch Hauptmenü-Aktionen mit benutzerdefinierten Makros.
        Unterstützt unbegrenzt tief verschachtelte Submenüs (Rekursion) und 
        schützt das Kernmenü 'Datei'.
        """
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        i18n = main_window._services.get("i18n")
        lang = getattr(i18n, "_current_lang", "de")
        
        menu_structure = cfg.UI_SCHEMA.get("menu_structure", {})
        action_items = {} # Anzeige-Name -> (Menu_ID, Item_Dict)

        def _extract_actions_recursive(items_list, parent_label_path, menu_id):
            """Durchwandert rekursiv alle Menüebenen, um Action-Items zu finden."""
            for item in items_list:
                item_type = item.get("type")
                item_id = item.get("id")
                
                # Lokalisierung des aktuellen Eintrags
                localized_item = i18n.text(item_id) if i18n else item_id
                current_path = f"{parent_label_path} -> {localized_item}"
                
                if item_type == "action":
                    display_label = f"{current_path} ({item_id})"
                    action_items[display_label] = (menu_id, item)
                    
                elif item_type == "submenu" and "items" in item:
                    # Tiefer in die Schachtelung eintauchen
                    _extract_actions_recursive(item["items"], current_path, menu_id)

        # Chronologischer WYSIWYG-Scan über alle Hauptmenüs
        for menu_id, menu_config in menu_structure.items():
            # ABSOLUTES SCHUTZSCHILD: Das komplette 'Datei'-Kernmenü wird ignoriert
            if menu_id == "file" or menu_config.get("i18n_key") == "menu.file":
                continue
                
            menu_key = menu_config.get("i18n_key", f"menu.{menu_id}")
            localized_menu = i18n.text(menu_key) if i18n else menu_id.upper()
            
            if "items" in menu_config:
                _extract_actions_recursive(menu_config["items"], localized_menu, menu_id)

        if not action_items:
            title_empty = i18n.text("dialog.title.no_entries") if i18n else ("Keine Einträge" if lang == "de" else "No Entries")
            msg_empty = "Es wurden keine konfigurierbaren Benutzer-Menüeinträge im System gefunden." if lang == "de" else "No configurable user menu items found in the system."
            QMessageBox.warning(main_window, title_empty, msg_empty)
            return

        # Dialog 1: Welchem Menüpunkt soll das Makro zugeordnet werden?
        title_sel_item = i18n.text("sidebar.item.assign_btn") if i18n else "Befehl zuordnen..."
        label_sel_item = "Ziel-Menüeintrag auswählen:" if lang == "de" else "Select target menu item:"
        
        chosen_item_label, ok1 = QInputDialog.getItem(
            main_window, title_sel_item, label_sel_item, list(action_items.keys()), 0, False
        )
        if not ok1 or not chosen_item_label:
            return
            
        target_menu_id, target_item_dict = action_items[chosen_item_label]

        # 2. SCHRITT: Das Verzeichnis commands_user dynamisch nach .py-Makros scannen
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_cmd_dir = os.path.join(base_dir, "business", "commands_user")
        
        available_macros = []
        if os.path.exists(user_cmd_dir):
            for filename in os.listdir(user_cmd_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    available_macros.append(filename)
                    
        available_macros.sort()

        if not available_macros:
            title_no_macro = "Keine Makros" if lang == "de" else "No Macros"
            msg_no_macro = f"Keine benutzerdefinierten Makros im Ordner '{user_cmd_dir}' gefunden." if lang == "de" else f"No user macros found in folder '{user_cmd_dir}'."
            QMessageBox.information(main_window, title_no_macro, msg_no_macro)
            return

        # Dialog 2: Welches Makro aus dem Ordner soll zugewiesen werden?
        label_sel_macro = "Verfügbares Benutzer-Makro auswählen:" if lang == "de" else "Select available user macro:"
        
        chosen_macro_file, ok2 = QInputDialog.getItem(
            main_window, title_sel_item, label_sel_macro, available_macros, 0, False
        )
        if not ok2 or not chosen_macro_file:
            return

        # 3. SCHRITT: Modul-Pfad für den dynamischen Klassen-Importer aufbereiten
        macro_module_name = chosen_macro_file.replace(".py", "")
        parts = macro_module_name.split('_')
        class_name_parts = [p.capitalize() for p in parts if p.lower() != 'cmd']
        expected_class_name = "".join(class_name_parts) + "Command"
        
        full_command_path = f"business.commands_user.{macro_module_name}.{expected_class_name}"

        # 4. SCHRITT: Transaktionale Aktualisierung & Live-Neuaufbau
        if "ui_state_manager" in main_window._services:
            main_window._services["ui_state_manager"].save_checkpoint()

        target_item_dict["command_class"] = full_command_path
        
        persistence = main_window._services.get("menu_persistence")
        if persistence and hasattr(persistence, "save_menus"):
            persistence.save_menus(cfg.UI_SCHEMA)

        if hasattr(main_window, "setup_ui"):
            main_window.setup_ui()

        msg_success = f"Makro '{expected_class_name}' erfolgreich mit '{target_item_dict['id']}' verknüpft." if lang == "de" else f"Macro '{expected_class_name}' successfully linked to '{target_item_dict['id']}'."
        main_window.statusBar().showMessage(msg_success, 4000)


    @staticmethod
    def _live_insert_widget(main_window, widget_type):
        """
        Platziert ein Excel-Steuerelement auf dem aktiven Tab und generiert/erweitert das Sammel-Makro.
        Garantiert die unzerbrechliche Persistenz des Typsystems auf der Festplatte.
        """
        from PyQt6.QtWidgets import QMessageBox, QInputDialog
        import uuid
        import infrastructure.cfg as cfg

        i18n = main_window._services["i18n"]
        current_tab_index = main_window._tabs.currentIndex()
        
        # Schutzschild: Auf dem Willkommens-Register (Index 0) darf nichts injiziert werden!
        if current_tab_index == 0:
            QMessageBox.warning(main_window, "Schutzschild", "Das Willkommens-Register ist geschützt und darf nicht modifiziert werden.")
            return
            
        active_tab_widget = main_window._tabs.widget(current_tab_index)
        # Ermittle die ID des aktuellen Tabs (z.B. "tab.extraction")
        tab_id = getattr(active_tab_widget, "tab_id", f"tab_{current_tab_index}")
        # Bereinige den Namen für den Dateinamen (Punkte durch Unterstriche ersetzen)
        clean_tab_name = tab_id.replace(".", "_")
        
        # 1. BILINGUALE ABFRAGE FÜR DIE BESCHRIFTUNG (Zwingend Deutsch und Englisch)
        lang = getattr(i18n, "_current_lang", "de")
        prompt_de = "Deutscher Platzhalter/Text:" if lang == "de" else "German label/placeholder text:"
        prompt_en = "Englischer Platzhalter/Text:" if lang == "de" else "English counterpart text:"
        
        text_de, ok1 = QInputDialog.getText(main_window, "VBA-Designer", prompt_de)
        if not ok1 or not text_de.strip(): return
        text_en, ok2 = QInputDialog.getText(main_window, "VBA-Designer", prompt_en, text=text_de.strip())
        if not ok2 or not text_en.strip(): return
        
        # =====================================================================
        # ARCHITEKTUR-REPARATUR: SNAPSHOT JETZT SCHIESSEN (VOR ALLEN ÄNDERUNGEN)
        # =====================================================================
        if "ui_state_manager" in main_window._services:
            main_window._services["ui_state_manager"].save_checkpoint()
        # =====================================================================

        # Einzigartige IDs generieren (Unzerbrechlicher UUID-Anker)
        elem_uuid = uuid.uuid4().hex[:8]
        elem_id = f"custom.{widget_type}.{elem_uuid}"
        unique_i18n_key = f"fields.dynamic.{elem_uuid}"
        
        # Übersetzungen dauerhaft im System registrieren
        i18n.update_or_append_key(key=unique_i18n_key, de_text=text_de.strip(), en_text=text_en.strip())
        
        # 2. DAS ERWEITERTE ELEMENT-WÖRTERBUCH FÜR DIE WIDGETFACTORY BAUEN
        macro_module_path = f"business.commands_user.cmd_{clean_tab_name}"
        event_method_name = f"on_{widget_type}_{elem_uuid}_changed"
        
        # =====================================================================
        # INTELIGENTES RASTER-SNAPPING (VBA-Style)
        # =====================================================================
        START_X = 25
        START_Y = 25
        ZEILEN_ABSTAND = 40  # Abstand für schmale Elemente (Buttons, Inputs)

        current_x = START_X
        current_y = START_Y

        # Standardgrößen für die Fabrik festlegen (Mehrzeilige Textfelder werden größer)
        default_w = 400 if widget_type in ["input_text", "text_viewer", "groupbox"] else 160
        default_h = 120 if widget_type in ["input_text", "text_viewer"] else 30

        # Wir scannen die bereits existierenden Elemente auf diesem Tab, 
        # um den nächsten freien Platz darunter zu ermitteln
        existing_elements = []
        for t_conf in cfg.UI_SCHEMA.get("tab_structure", []):
            if t_conf.get("id") == tab_id:
                existing_elements = t_conf.get("elements", [])
                break

        if existing_elements:
            max_y = START_Y
            for elem in existing_elements:
                # Wir holen die echten Fabrik-Koordinaten
                elem_y = elem.get("y", START_Y)
                elem_h = elem.get("height", 30)
                if (elem_y + elem_h) > max_y:
                    max_y = elem_y + elem_h
            
            # Das neue Element rückt sauber nach unten (Snapping)
            current_y = max_y + ZEILEN_ABSTAND

        # PERSISTENZ-SICHERUNG: Exakt passend für deine WidgetFactory-Keys!
        pure_element = {
            "type": str(widget_type),
            "id": str(elem_id),
            "macro_file": str(macro_module_path),
            "macro_event": str(event_method_name),
            "x": int(current_x),       # Passend zur Fabrik: 'x' statt 'geometry_x'
            "y": int(current_y),       # Passend zur Fabrik: 'y' statt 'geometry_y'
            "width": int(default_w),   # Passend zur Fabrik: 'width' statt 'geometry_w'
            "height": int(default_h)   # Passend zur Fabrik: 'height' statt 'geometry_h'
        }

        # Unterscheidung für i18n-Keys je nach Element-Typ (Label/Button vs. Eingabefelder)
        if widget_type in ["button", "checkbox", "radiobutton", "groupbox", "label"]:
            pure_element["i18n_key"] = unique_i18n_key
        else:
            pure_element["placeholder_i18n"] = unique_i18n_key
            
        # AUTOMATISCHE SAMMEL-CODEBLOCK GENERIERUNG (Der intelligente Excel-Style)
        IDEDesigner._append_or_create_tab_macro(clean_tab_name, event_method_name, text_de.strip())
        
        # =====================================================================
        # RAM-POOL SYNCHRONISATION & ZUSTANDS-SICHERUNG
        # =====================================================================
        tab_found = False
        for t_conf in cfg.UI_SCHEMA.get("tab_structure", []):
            if t_conf.get("id") == tab_id:
                if "elements" not in t_conf:
                    t_conf["elements"] = []
                t_conf["elements"].append(pure_element)
                tab_found = True
                break

        # KORREKTUR: Stellt hierarchische Integrität sicher, ohne bestehende Register zu überschreiben
        if not tab_found:
            if "tab_structure" not in cfg.UI_SCHEMA:
                cfg.UI_SCHEMA["tab_structure"] = [
                    {
                        "id": "tab.welcome",
                        "i18n_key": "tabs.welcome.title",
                        "label": "Welcome",
                        "elements": []
                    }
                ]
            
            # Neues Register sicher an das bestehende Array anfügen
            cfg.UI_SCHEMA["tab_structure"].append({
                "id": tab_id,
                "i18n_key": f"tabs.custom.{tab_id.replace('tab_custom_', '')}.title",
                "label": text_de.strip(),
                "elements": [pure_element]
            })

        # FESTPLATTEN-RETTUNG: Erzwingt das sofortige physische Schreiben in die JSON-Datei
        persistence = main_window._services.get("menu_persistence")
        if persistence and hasattr(persistence, "save_menus"):
            persistence.save_menus(cfg.UI_SCHEMA)
            
        # 3. LIVE-RENDER INJECTION & I18N-ANMELDUNG
        if hasattr(active_tab_widget, "add_element_live"):
            active_tab_widget.add_element_live(pure_element)
            
            # Registriert das Live-Widget sofort im Übersetzungsdienst für Sprachwechsel zur Laufzeit
            if hasattr(active_tab_widget, "element_registry"):
                created_widget = active_tab_widget.element_registry.get(elem_id)
                if created_widget:
                    w_type = "placeholder" if widget_type in ["input_line", "input_text", "text_viewer"] else "button"
                    i18n.register(created_widget, w_type, unique_i18n_key)
        
        # Aktualisiert die Anzeige direkt auf die aktuelle Sprache
        i18n.translate_all()
            
        main_window.statusBar().showMessage(f"Baustein '{text_de.strip()}' erfolgreich platziert und permanent gespeichert.", 4000)


    
    @staticmethod
    def _append_or_create_tab_macro(clean_tab_name, event_method_name, element_label):
        """
        Prüft, ob das Sammel-Modul für das Tab existiert.
        Wenn nein, wird es erschaffen. Wenn ja, wird das neue Event angehängt (Once-Only-Prinzip).
        Inklusive der bilingualen Entwickler-Sonde!
        """
        # Pfad zum commands_user-Ordner ermitteln
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_cmd_dir = os.path.join(base_dir, "business", "commands_user")
        if not os.path.exists(user_cmd_dir):
            os.makedirs(user_cmd_dir)
            
        filename = f"cmd_{clean_tab_name}.py"
        file_path = os.path.join(user_cmd_dir, filename)
        class_name = f"TabControl_{clean_tab_name}"
        
        # Das neue Event-Skelett mit deiner sprachneutralen Entwickler-Sonde
        # Wichtig: Die 4 Leerzeichen vor 'def' sorgen für die richtige Position in der Ziel-Klasse!
        event_code_block = f"""
    def {event_method_name}(self, event_data):
        \"\"\"Live-Event für das Steuerelement: {element_label}
        HINWEIS FÜR ENTWICKLER: Fügen Sie hier Ihre Business-Logik ein.
        \"\"\"
        from PyQt6.QtWidgets import QMessageBox

        # 1. i18n-Service aus dem Hauptfenster holen
        i18n = self.main_window._services.get("i18n")
        
        if i18n:
            # 2. Bilinguale Texte mit Platzhaltern aus den JSON-Dateien laden
            title = i18n.text("ide.sonde.title") or "ClioGraph IDE Event-Sonde"
            line1 = (i18n.text("ide.sonde.success") or "Event '{{event}}' erfolgreich ausgelöst!").format(event="{event_method_name}")
            line2 = (i18n.text("ide.sonde.element") or "Steuerelement: '{{label}}'").format(label="{element_label}")
            line3 = (i18n.text("ide.sonde.data") or "Übergebene Daten: {{data}}").format(data=str(event_data))
            line4 = (i18n.text("ide.sonde.hint") or "Bitte bearbeiten Sie das Modul: '{{module}}'").format(module="business/commands_user/{filename}")
            
            msg = f"{{line1}}\\n\\n{{line2}}\\n{{line3}}\\n\\n{{line4}}"
        else:
            # Fallback-Sicherung
            title = "ClioGraph IDE Event-Sonde"
            msg = f"Event '{event_method_name}' erfolgreich ausgelöst!\\nDaten: {{event_data}}"
            
        QMessageBox.information(self.main_window, title, msg)
"""

        if not os.path.exists(file_path):
            # FALL A: Datei existiert noch nicht -> Komplett neu anlegen mit Klassen-Kopf
            header_code = f"""# -*- coding: utf-8 -*-
\"\"\"Automatisch generiertes Sammel-Makro für das Register: {clean_tab_name}\"\"\"
from PyQt6.QtWidgets import QMessageBox

class {class_name}:
    \"\"\"Zentrales Steuerungsobjekt für alle Live-Events dieser Registerkarte.\"\"\"
    def __init__(self, main_window):
        self.main_window = main_window
"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(header_code + event_code_block)
            print(f" [IDE] Sammel-Makrodatei {filename} neu angelegt.")
        else:
            # FALL B: Datei existiert bereits -> Das neue Event einfach unten anhängen
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(event_code_block)
            print(f" [IDE] Event {event_method_name} an {filename} angehängt.")

    
    @staticmethod
    def _live_move_element(main_window, direction):
        """
        Sortiert die Steuerelemente innerhalb der JSON-Struktur des aktiven Tabs um.
        Dient als stabile Zwischenstufe vor dem PySide6-Refactoring.
        """
        current_tab_index = main_window._tabs.currentIndex()
        if current_tab_index == 0:
            return  # Schutzschild Willkommens-Tab
            
        active_tab_widget = main_window._tabs.widget(current_tab_index)
        tab_id = getattr(active_tab_widget, "tab_id", None)
        if not tab_id:
            return
            
        # Such das Tab im globalen UI_SCHEMA
        for t_conf in cfg.UI_SCHEMA.get("tab_structure", []):
            if t_conf.get("id") == tab_id and "elements" in t_conf:
                elems = t_conf["elements"]
                if len(elems) < 2:
                    return
                    
                # Hier nehmen wir für die Vorstufe das letzte Element als Referenz
                idx = len(elems) - 1
                new_idx = idx + direction
                
                if 0 <= new_idx < len(elems):
                    # Elemente fliegend im RAM-Array tauschen
                    elems[idx], elems[new_idx] = elems[new_idx], elems[idx]
                    
                    # Auf Platte sichern
                    persistence = main_window._services.get("menu_persistence")
                    if persistence and hasattr(persistence, "save_menus"):
                        persistence.save_menus(cfg.UI_SCHEMA)
                    
                    # HIER KORRIGIERT: Kein main_window.setup_ui() mehr!
                    # Wir aktualisieren nur das Layout des betroffenen Tabs
                    if hasattr(active_tab_widget, "update"):
                        active_tab_widget.update()
                    main_window.statusBar().showMessage("Position des Elements im Schema geändert.", 2000)
                break

    @staticmethod
    def _live_genai_build(main_window, prompt_text):
        """Schnittstelle für das deklarative Prompt-to-Widget System."""
        if not prompt_text.strip(): return
        QMessageBox.information(main_window, "GenAI-Builder", f"Injektions-Prompt erfasst:\\n'{prompt_text}'\\n\\nDie LLM-Struktur-Injektion wird im nächsten Schritt angebunden.")

    @staticmethod
    def _live_genai_build(main_window, prompt_text):
        """
        Generischer GenAI-Layout-Injektor für das Open-Source-Basisframework.
        Analysiert den Prompt rein auf strukturelle Steuerelemente und stapelt diese bilingual.
        """
        if not prompt_text.strip(): 
            return

        from PyQt6.QtWidgets import QMessageBox
        import uuid
        import infrastructure.cfg as cfg

        i18n = main_window._services["i18n"]
        lang = getattr(i18n, "_current_lang", "de")
        prompt_lower = prompt_text.lower()

        # 1. Transaktions-Snapshot für unzerbrechliches Undo/Redo schießen
        if "ui_state_manager" in main_window._services:
            main_window._services["ui_state_manager"].save_checkpoint()

        # 2. Neues, leeres Register mit einer eindeutigen UUID initialisieren
        tab_uuid = uuid.uuid4().hex[:8]
        tab_id = f"tab.genai_{tab_uuid}"
        clean_tab_name = tab_id.replace(".", "_")
        unique_tab_title_key = f"tabs.custom.{tab_uuid}.title"

        # Neutraler Framework-Standardtitel für das neue Register
        title_de = f"KI-Layout ({tab_uuid})"
        title_en = f"AI Layout ({tab_uuid})"
        i18n.update_or_append_key(key=unique_tab_title_key, de_text=title_de, en_text=title_en)

        # 3. Absolut generisches Text-Parsing für universelle Framework-Widgets
        # Wir definieren Erkennungsmuster für die Standard-Typen deiner WidgetFactory
        detected_types = []
        
        # Aufteilung des Prompts anhand von Kommas oder "und", um einzelne Feldwünsche zu isolieren
        segments = prompt_lower.replace(" und ", ",").split(",")
        
        for segment in segments:
            seg = segment.strip()
            if not seg: continue
            
            # Typ-Erkennung basierend auf universellen Begriffen
            w_type = "input_line" # Standard-Fallback
            label_suggestion_de = "Eingabefeld"
            label_suggestion_en = "Input Field"
            
            if "button" in seg or "schaltfläche" in seg or "klick" in seg or "speichern" in seg:
                w_type = "button"
                label_suggestion_de = "Aktion ausführen" if "speichern" not in seg else "Speichern"
                label_suggestion_en = "Execute Action" if "speichern" not in seg else "Save"
            elif "textbereich" in seg or "mehrzeilig" in seg or "adresse" in seg or "textarea" in seg:
                w_type = "input_text"
                label_suggestion_de = "Textbereich" if "adresse" not in seg else "Adresse"
                label_suggestion_en = "Text Area" if "adresse" not in seg else "Address"
            elif "auswahl" in seg or "dropdown" in seg or "combobox" in seg:
                w_type = "combobox"
                label_suggestion_de = "Auswahlfeld"
                label_suggestion_en = "Dropdown Field"
            elif "titel" in seg or "überschrift" in seg or "label" in seg:
                w_type = "label"
                label_suggestion_de = "Überschrift"
                label_suggestion_en = "Headline"
            elif "name" in seg:
                w_type = "input_line"
                label_suggestion_de = "Name / Vorname" if "vorname" in seg else "Name"
                label_suggestion_en = "First / Last Name" if "vorname" in seg else "Name"
            elif "login" in seg or "benutzer" in seg:
                w_type = "input_line"
                label_suggestion_de = "Benutzername / Login"
                label_suggestion_en = "Username / Login"

            detected_types.append((w_type, label_suggestion_de, label_suggestion_en))

        # Falls gar nichts erkannt wurde, injizieren wir ein Standard-Skelett als Demo
        if not detected_types:
            detected_types = [
                ("label", "Generierte Oberfläche", "Generated Interface"),
                ("input_line", "Eingabe...", "Input..."),
                ("button", "Bestätigen", "Confirm")
            ]

        # 4. Geometrie-Layout-Berechnung: Elemente sauber untereinander stapeln (VBA-Style)
        generated_elements = []
        START_X = 25
        START_Y = 25
        SPACING = 15
        current_y = START_Y

        for w_type, lbl_de, lbl_en in detected_types:
            elem_uuid = uuid.uuid4().hex[:6]
            unique_elem_key = f"fields.genai.{elem_uuid}"
            
            # Zweisprachigen Text für das Widget registrieren
            i18n.update_or_append_key(key=unique_elem_key, de_text=lbl_de, en_text=lbl_en)
            
            # Standardgrößen festlegen (Mehrzeilige Textfelder werden größer dimensioniert)
            width = 400 if w_type in ["input_text", "text_viewer", "groupbox"] else 200
            height = 120 if w_type in ["input_text", "text_viewer"] else 30
            
            elem_dict = {
                "type": w_type,
                "id": f"custom.{w_type}.{elem_uuid}",
                "x": int(START_X),
                "y": int(current_y),
                "width": int(width),
                "height": int(height)
            }
            
            # i18n-Schlüssel je nach Typ an die korrekte Eigenschaft binden
            if w_type in ["button", "checkbox", "radiobutton", "groupbox", "label"]:
                elem_dict["i18n_key"] = unique_elem_key
            else:
                elem_dict["placeholder_i18n"] = unique_elem_key

            # Makro-Verknüpfung und Code-Templates für interaktive Elemente erstellen
            if w_type in ["button", "input_line", "input_text", "combobox", "checkbox", "radiobutton"]:
                event_name = f"on_{w_type}_{elem_uuid}_triggered"
                elem_dict["macro_file"] = f"business.commands_user.cmd_{clean_tab_name}"
                elem_dict["macro_event"] = event_name
                
                # Leere Python-Methode im commands_user-Ordner vorbereiten
                IDEDesigner._append_or_create_tab_macro(clean_tab_name, event_name, f"GenAI {w_type}")

            generated_elements.append(elem_dict)
            current_y += height + SPACING # Nächstes Element nach unten verschieben

        # 5. Neues Register im globalen RAM-Schema registrieren
        new_tab_config = {
            "id": tab_id,
            "i18n_key": unique_tab_title_key,
            "label": title_de,
            "layout_type": "form",
            "elements": generated_elements
        }
        cfg.UI_SCHEMA["tab_structure"].append(new_tab_config)

        # 6. Permanente Sicherung auf der Festplatte (DAL-Schicht)
        persistence = main_window._services.get("menu_persistence")
        if persistence and hasattr(persistence, "save_menus"):
            persistence.save_menus(cfg.UI_SCHEMA)

        # 7. Live-UI-Refresher des Hauptfensters ausführen
        if hasattr(main_window, "setup_ui"):
            main_window.setup_ui()

        # Fokus direkt auf das neu erstellte Register setzen
        main_window._tabs.setCurrentIndex(main_window._tabs.count() - 2)

        msg_success = f"Generisches Layout erfolgreich injiziert." if lang == "de" else f"Generic layout successfully injected."
        main_window.statusBar().showMessage(msg_success, 5000)
