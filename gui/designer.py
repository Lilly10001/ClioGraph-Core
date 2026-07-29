# -*- coding: utf-8 -*-
"""
Presentation Layer: Integriertes Kontrollzentrum als linke Navigationsleiste
(Sidebar) mit funktionalen Gruppen für Hauptmenü, Items und Register.
Erweitert um Undo/Redo-Schutz und Positionsverschiebungen.
Bereinigt: Makro-Zuweisung in die Entwicklertools ausgelagert.
"""

import uuid 
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt
import infrastructure.cfg as cfg

class MenuDesigner:
    """Kapselt alle Laufzeit-Operationen zur Modifikation des UI-Schemas in einer linken Sidebar."""
 
    @staticmethod
    def inject_designer_sidebar_at(main_window, target_widget):
        """Erstellt das Layout des System-Designers innerhalb des übergebenen Ziel-Widgets."""
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        target_widget.setLayout(panel_layout)
 
        # INHALTS-BEREICH
        main_window._designer_content = QWidget()
        main_window._designer_content.setStyleSheet("""
        QWidget { border: none; background: transparent; }
        QLabel.group_title { font-weight: bold; color: #6c757d; font-size: 11px; margin-top: 8px; margin-bottom: 2px; }
        QPushButton { background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 6px; text-align: left; font-size: 11px; }
        QPushButton:hover { background-color: #e9ecef; }
        """)
 
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 5, 10, 10)
        content_layout.setSpacing(5)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_window._designer_content.setLayout(content_layout)
 
        def create_separator():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("color: #ced4da; margin-top: 4px; margin-bottom: 4px;")
            return line
 
        i18n = main_window._i18n
 
        # ---------------------------------------------------------------------
        # SEKTION 0: SAFETY ZONE (Undo / Redo ganz oben)
        # ---------------------------------------------------------------------
        lbl_safety = QLabel("SICHERHEITS-VERLAUF")
        lbl_safety.setStyleSheet("font-weight: bold; color: #1a73e8; font-size: 10px; margin-top: 5px;")
        content_layout.addWidget(lbl_safety)
        
        safety_layout = QHBoxLayout()
        btn_undo = QPushButton()
        btn_redo = QPushButton()
 
        i18n.register(btn_undo, "button", "sidebar.safety.undo")
        i18n.register(btn_redo, "button", "sidebar.safety.redo")
 
        btn_undo.clicked.connect(lambda: MenuDesigner._trigger_undo(main_window))
        btn_redo.clicked.connect(lambda: MenuDesigner._trigger_redo(main_window))
        safety_layout.addWidget(btn_undo)
        safety_layout.addWidget(btn_redo)
        content_layout.addLayout(safety_layout)
        content_layout.addWidget(create_separator())

        # ---------------------------------------------------------------------
        # SEKTION 1: HAUPTMENÜ
        # ---------------------------------------------------------------------
        lbl_g1 = QLabel()
        i18n.register(lbl_g1, "button", "sidebar.menu.group")
        content_layout.addWidget(lbl_g1)
 
        btn_add_menu = QPushButton()
        i18n.register(btn_add_menu, "button", "sidebar.menu.add")
        btn_add_menu.clicked.connect(main_window.create_new_main_menu)
        content_layout.addWidget(btn_add_menu)
 
        btn_del_menu = QPushButton()
        i18n.register(btn_del_menu, "button", "sidebar.menu.delete")
        btn_del_menu.clicked.connect(lambda: MenuDesigner._live_remove_main_menu(main_window))
        content_layout.addWidget(btn_del_menu)
 
        btn_ren_menu = QPushButton()
        i18n.register(btn_ren_menu, "button", "sidebar.menu.rename")
        btn_ren_menu.clicked.connect(lambda: MenuDesigner._live_rename_main_menu(main_window))
        content_layout.addWidget(btn_ren_menu)
 
        move_layout = QHBoxLayout()
        move_layout.setSpacing(4)
        btn_move_left = QPushButton()
        btn_move_right = QPushButton()
        i18n.register(btn_move_left, "button", "sidebar.menu.move_left")
        i18n.register(btn_move_right, "button", "sidebar.menu.move_right")
        btn_move_left.clicked.connect(lambda: MenuDesigner._live_move_menu(main_window, -1))
        btn_move_right.clicked.connect(lambda: MenuDesigner._live_move_menu(main_window, 1))
        move_layout.addWidget(btn_move_left)
        move_layout.addWidget(btn_move_right)
        content_layout.addLayout(move_layout)
        content_layout.addWidget(create_separator())

        # ---------------------------------------------------------------------
        # SEKTION 2: SCHALTFLÄCHEN (ITEMS)
        # ---------------------------------------------------------------------
        lbl_g2 = QLabel()
        i18n.register(lbl_g2, "button", "sidebar.item.group")
        content_layout.addWidget(lbl_g2)
 
        btn_add_item = QPushButton()
        i18n.register(btn_add_item, "button", "sidebar.item.add")
        btn_add_item.clicked.connect(lambda: MenuDesigner._live_add_menu_item(main_window))
        content_layout.addWidget(btn_add_item)
 
        btn_del_item = QPushButton()
        i18n.register(btn_del_item, "button", "sidebar.item.delete")
        btn_del_item.clicked.connect(lambda: MenuDesigner._live_remove_menu_item(main_window))
        content_layout.addWidget(btn_del_item)
 
        btn_ren_item = QPushButton()
        i18n.register(btn_ren_item, "button", "sidebar.item.rename")
        btn_ren_item.clicked.connect(lambda: MenuDesigner._live_rename_menu_item(main_window))
        content_layout.addWidget(btn_ren_item)
 
        # HIER WURDE DER REINIGER REINGESETZT: KERN-KORREKTUR ERFOLGT (btn_macro ENTFERNT!)
 
        item_move_layout = QHBoxLayout()
        btn_item_up = QPushButton()
        btn_item_down = QPushButton()
        i18n.register(btn_item_up, "button", "sidebar.item.move_up")
        i18n.register(btn_item_down, "button", "sidebar.item.move_down")
        btn_item_up.clicked.connect(lambda: MenuDesigner._live_move_menu_item(main_window, -1))
        btn_item_down.clicked.connect(lambda: MenuDesigner._live_move_menu_item(main_window, 1))
        item_move_layout.addWidget(btn_item_up)
        item_move_layout.addWidget(btn_item_down)
        content_layout.addLayout(item_move_layout)
        content_layout.addWidget(create_separator())

        # ---------------------------------------------------------------------
        # SEKTION 3: REGISTERKARTEN (TABS)
        # ---------------------------------------------------------------------
        lbl_g3 = QLabel()
        i18n.register(lbl_g3, "button", "sidebar.tab.group")
        content_layout.addWidget(lbl_g3)
 
        btn_add_tab = QPushButton()
        i18n.register(btn_add_tab, "button", "sidebar.tab.add")
        btn_add_tab.clicked.connect(lambda: MenuDesigner._live_add_new_tab(main_window))
        content_layout.addWidget(btn_add_tab)
 
        btn_del_tab = QPushButton()
        i18n.register(btn_del_tab, "button", "sidebar.tab.delete")
        btn_del_tab.clicked.connect(lambda: MenuDesigner._live_remove_tab(main_window))
        content_layout.addWidget(btn_del_tab)

        btn_ren_tab = QPushButton()
        i18n.register(btn_ren_tab, "button", "sidebar.tab.rename")
        btn_ren_tab.clicked.connect(lambda: MenuDesigner._live_rename_tab(main_window))
        content_layout.addWidget(btn_ren_tab)
 
        tab_move_layout = QHBoxLayout()
        btn_tab_left = QPushButton()
        btn_tab_right = QPushButton()
        i18n.register(btn_tab_left, "button", "sidebar.tab.move_left")
        i18n.register(btn_tab_right, "button", "sidebar.tab.move_right")
        btn_tab_left.clicked.connect(lambda: MenuDesigner._live_move_tab(main_window, -1))
        btn_tab_right.clicked.connect(lambda: MenuDesigner._live_move_tab(main_window, 1))
        tab_move_layout.addWidget(btn_tab_left)
        tab_move_layout.addWidget(btn_tab_right)
        content_layout.addLayout(tab_move_layout)
 
        panel_layout.addWidget(main_window._designer_content)
        i18n.translate_all()

    # -------------------------------------------------------------------------
    # Steuerung aller Auswahldialoge für Hauptmenüs, Items und Tabs (einheitlich & zentral)
    # -------------------------------------------------------------------------
    @staticmethod
    def _show_generic_selection_dialog(win, section_prefix, items_dict, custom_title=None):
        """
        Zentraler, generischer Dialog für ALLE Sektionen.
        Nutzt entweder den custom_title für den blauen Balken oder fällt auf die Gruppe zurück.
        """
        from PyQt6.QtWidgets import QInputDialog
 
        if custom_title:
            dialog_title = custom_title
        else:
            dialog_title = win._i18n.text(f"sidebar.{section_prefix}.group") or section_prefix.upper()
 
        fallback_label = f"{win._i18n.text(f'sidebar.{section_prefix}.group') or section_prefix.upper()} wählen:"
        raw_translation = win._i18n.text(f"dialog.{section_prefix}.select_label")
 
        if not raw_translation or raw_translation == f"dialog.{section_prefix}.select_label":
            label_text = fallback_label
        else:
            label_text = raw_translation
 
        display_names = list(items_dict.keys())
 
        chosen_name, ok = QInputDialog.getItem(
            win, 
            dialog_title, 
            label_text, 
            display_names, 
            0, 
            False
        )
        if ok and chosen_name:
            return items_dict[chosen_name]
        return None

    # -------------------------------------------------------------------------
    # UNDO / REDO TRIGGER
    # -------------------------------------------------------------------------
    
        # -------------------------------------------------------------------------
    # UNDO / REDO TRIGGER
    # -------------------------------------------------------------------------
    @staticmethod
    def _trigger_undo(win):
        if "ui_state_manager" in win._services:
            # 1. Merke dir das aktuell aktive Register, BEVOR wir alles abreißen
            current_tab_idx = win._tabs.currentIndex() if hasattr(win, "_tabs") else 0
            
            if win._services["ui_state_manager"].undo_action():
                win.setup_ui()
                
                # 2. Springe sofort wieder auf das Register zurück
                if hasattr(win, "_tabs") and current_tab_idx < win._tabs.count():
                    win._tabs.setCurrentIndex(current_tab_idx)
                
                # === REPARATUR: SIGNALE DER SIDEBARS NEU VERDRAHTEN ===
                from gui.designer import MenuDesigner
                if hasattr(win, "ui") and hasattr(win.ui, "sidebar_container"):
                    MenuDesigner.inject_sidebar_at(win, win.ui.sidebar_container)
                
                msg = win._i18n.text("notification.undo.success") or "Rückgängig erfolgreich durchgeführt."
                win.statusBar().showMessage(msg, 2000)

    @staticmethod
    def _trigger_redo(win):
        if "ui_state_manager" in win._services:
            # 1. Merke dir das aktuell aktive Register, BEVOR wir alles abreißen
            current_tab_idx = win._tabs.currentIndex() if hasattr(win, "_tabs") else 0
            
            if win._services["ui_state_manager"].redo_action():
                win.setup_ui()
                
                # 2. Springe sofort wieder auf das Register zurück
                if hasattr(win, "_tabs") and current_tab_idx < win._tabs.count():
                    win._tabs.setCurrentIndex(current_tab_idx)
                
                # === REPARATUR: SIGNALE DER SIDEBARS NEU VERDRAHTEN ===
                from gui.designer import MenuDesigner
                if hasattr(win, "ui") and hasattr(win.ui, "sidebar_container"):
                    MenuDesigner.inject_sidebar_at(win, win.ui.sidebar_container)
                
                msg = win._i18n.text("notification.redo.success") or "Wiederholen erfolgreich durchgeführt."
                win.statusBar().showMessage(msg, 2000)


    # -------------------------------------------------------------------------
    # OPERATIVE LOGIK MIT SCHUTZSCHILDEN (HAUPTMENÜ)
    # -------------------------------------------------------------------------
    @staticmethod
    def _live_remove_main_menu(win):
        """Löscht ein Hauptmenü nach erfolgreicher, bilingualer Sicherheitsabfrage."""
        target_uuid = MenuDesigner._select_main_menu_dialog(win, action_type="delete")
        if not target_uuid:
            return
        # Absoluter Schutz des Kern-Menüs (Datei darf niemals gelöscht werden)
        if target_uuid == "file" or cfg.UI_SCHEMA["menu_structure"][target_uuid].get("i18n_key") == "menu.file":
            QMessageBox.warning(win, win._i18n.text("msg.protection.title"), win._i18n.text("msg.protection.core_deny"))
            return
            
        i18n_key = cfg.UI_SCHEMA["menu_structure"][target_uuid].get("i18n_key", f"menu.{target_uuid}")
        localized_menu_name = win._i18n.text(i18n_key)
        dialog_title = win._i18n.text("sidebar.menu.delete") or "Hauptmenü löschen"
        raw_message = win._i18n.text("dialog.menu.delete.confirm") or "Möchten Sie das Menü '{0}' wirklich löschen?"
        formatted_message = raw_message.format(localized_menu_name)
        
        reply = QMessageBox.question(
            win, 
            dialog_title, 
            formatted_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
 
        if reply == QMessageBox.StandardButton.Yes:
            if "ui_state_manager" in win._services:
                win._services["ui_state_manager"].save_checkpoint()
            del cfg.UI_SCHEMA["menu_structure"][target_uuid]
 
            if "menu_order" in cfg.UI_SCHEMA and target_uuid in cfg.UI_SCHEMA["menu_order"]:
                cfg.UI_SCHEMA["menu_order"].remove(target_uuid)
            win.setup_ui()
            MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_rename_main_menu(win):
        """Benennt ein Hauptmenü über den zentralen, bilingualen Dialog um."""
        target_uuid = MenuDesigner._select_main_menu_dialog(win, action_type="rename")
        if not target_uuid:
            return
 
        menu_data = cfg.UI_SCHEMA["menu_structure"][target_uuid]
        if target_uuid == "file" or menu_data.get("i18n_key") == "menu.file":
            QMessageBox.warning(win, win._i18n.text("msg.protection.title"), win._i18n.text("msg.protection.core_deny"))
            return
        i18n_key = menu_data.get("i18n_key")
        alter_de = win._i18n.text(i18n_key)
        specific_title = win._i18n.text("sidebar.menu.rename") or "Hauptmenü umbenennen"
 
        neuer_de, ok1 = QInputDialog.getText(win, specific_title, "DEUTSCH / GERMAN:", text=alter_de)
        if not ok1 or not neuer_de.strip(): return
 
        suggested_en = neuer_de.strip()
        neuer_en, ok2 = QInputDialog.getText(win, specific_title, "ENGLISH / ENGLISCH:", text=suggested_en)
        if not ok2 or not neuer_en.strip(): return
        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()
 
        win._i18n.update_or_append_key(key=i18n_key, de_text=neuer_de.strip(), en_text=neuer_en.strip())
        win.setup_ui()
        MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_move_menu(win, direction):
        """Verschiebt das aktive Hauptmenü direkt im Schema ohne störenden Dialog."""
        import infrastructure.cfg as cfg
        
        # 1. Ermittle die Ziel-UUID des Menüs aus dem Fenster-Gedächtnis
        target_uuid = getattr(win, "_active_menu_uuid", None)
        order = cfg.UI_SCHEMA.get("menu_order", list(cfg.UI_SCHEMA["menu_structure"].keys()))
        
        # Fallback: Wenn nichts gesetzt oder gültig ist, nehmen wir das erste dynamische Menü
        if not target_uuid or target_uuid not in order:
            dynamic_menus = [k for k in order if k != "file"]
            if not dynamic_menus:
                return  # Keine verschiebbaren Menüs vorhanden
            target_uuid = dynamic_menus[0]

        # Absoluter Schutz des Datei-Menüs
        if target_uuid == "file" or cfg.UI_SCHEMA["menu_structure"][target_uuid].get("i18n_key") == "menu.file":
            return

        # Sicherheitsanker: 'file' muss zwingend auf Index 0 bleiben
        if "file" in order and order.index("file") != 0:
            order.remove("file")
            order.insert(0, "file")
            
        idx = order.index(target_uuid)
        new_idx = idx + direction
        
        # 2. Grenzen prüfen (Darf nicht auf Index 0 rutschen!)
        if 1 <= new_idx < len(order):
            if "ui_state_manager" in win._services:
                win._services["ui_state_manager"].save_checkpoint()
            
            # Direkter Swap im Schema-Array
            order[idx], order[new_idx] = order[new_idx], order[idx]
            cfg.UI_SCHEMA["menu_order"] = order
            
            # Benutzeroberfläche sofort live und flüssig neu zeichnen
            win.setup_ui()
            
            # Fokus für fortlaufendes Klicken auf diesem Menü halten
            win._active_menu_uuid = target_uuid
            
            MenuDesigner._save_schema_to_persistence(win)


    # -------------------------------------------------------------------------
    # ZENTRALE HILFSMETHODEN (Once-Only-Prinzip & Kaskadenschutz für Items)
    # -------------------------------------------------------------------------
    @staticmethod
    def _discover_all_menus_nested(win) -> dict:
        """Sammelt alle Haupt- und Submenüs rekursiv. Schützt das Datei-Menü."""
        mapping = {}
 
        def find_recursive(menu_dict):
            for key, data in menu_dict.items():
                if key == "file" or data.get("i18n_key") == "menu.file":
                    continue
                i18n_key = data.get("i18n_key", f"menu.{key}")
                name = win._i18n.text(i18n_key)
 
                display_str = f" Hauptmenü: {name}" if not key.startswith("dynamic.") else f" ↳ Submenü: {name}"
                mapping[display_str] = key
 
                for item in data.get("items", []):
                    if item.get("type") == "submenu":
                        find_recursive({item["id"]: {"i18n_key": item["id"], "items": item.get("items", [])}})
 
        find_recursive(cfg.UI_SCHEMA.get("menu_structure", {}))
        return mapping

    @staticmethod
    def _discover_all_items_nested(win, filter_type=None) -> dict:
        """Sammelt alle Items strikt entlang der visuellen Reihenfolge (menu_order) mit echten WYSIWYG-Texten."""
        import infrastructure.cfg as cfg
        mapping = {}
        
        def find_recursive(items_list, parent_path_str):
            for item in items_list:
                item_id = item["id"]
                if item_id.startswith("menu.file.") or item_id.startswith("dynamic.file."):
                    continue
                    
                item_type = item.get("type", "action")
                
                # --- DIE RETTUNG: Wir zwingen das i18n-System, den AKTUELLEN Text live zu holen ---
                localized_name = win._i18n.text(item_id)
                
                # Falls i18n fehlschlägt oder den Key als Text zurückgibt, säubern wir den Fallback
                if not localized_name or localized_name == item_id:
                    localized_name = item_id.split(".")[-1].replace("_", " ").title()
                
                if filter_type == "action" and item_type == "submenu":
                    find_recursive(item.get("items", []), f"{parent_path_str} ↳ {localized_name}")
                    continue
                    
                if filter_type and item_type != filter_type:
                    if item_type == "submenu":
                        find_recursive(item.get("items", []), f"{parent_path_str} ↳ {localized_name}")
                    continue
                    
                type_label = "Knopf" if item_type == "action" else "Untermenü"
                
                # WYSIWYG-Optimierung: Wir entfernen die verwirrende rohe ID in den Klammern am Ende!
                display_str = f"[{parent_path_str}] ↳ [{type_label}] {localized_name}"
                
                # Eindeutigkeit sichern, falls zwei Knöpfe exakt gleich heißen
                counter = 1
                base_display_str = display_str
                while display_str in mapping:
                    display_str = f"{base_display_str} ({counter})"
                    counter += 1
                
                mapping[display_str] = (items_list, item)
                
                if item_type == "submenu":
                    find_recursive(item.get("items", []), f"{parent_path_str} ↳ {localized_name}")
                    
        order = cfg.UI_SCHEMA.get("menu_order", list(cfg.UI_SCHEMA["menu_structure"].keys()))
        for m_key in order:
            if m_key == "file" or m_key not in cfg.UI_SCHEMA["menu_structure"]:
                continue
                
            m_data = cfg.UI_SCHEMA["menu_structure"][m_key]
            if m_data.get("i18n_key") == "menu.file":
                continue
                
            main_menu_name = win._i18n.text(m_data.get("i18n_key", f"menu.{m_key}"))
            find_recursive(m_data.get("items", []), f"Hauptmenü: {main_menu_name}")
            
        return mapping
   
    # -------------------------------------------------------------------------
    # OPERATIVE LOGIK: SCHALTFLÄCHEN (ITEMS) – KASKADIEREND & VEREINHEITLICHT
    # -------------------------------------------------------------------------
    @staticmethod
    def _live_add_menu_item(win):
        """Erzeugt ein neues Item in einem wählbaren Haupt- oder Submenü."""
        menu_mapping = MenuDesigner._discover_all_menus_nested(win)
        if not menu_mapping: 
            return
 
        order = cfg.UI_SCHEMA.get("menu_order", [])
        def get_sort_key(display_name):
            m_uuid = menu_mapping[display_name]
            if m_uuid in order:
                return (order.index(m_uuid), 0, display_name)
            for idx, main_uuid in enumerate(order):
                pure_id = main_uuid.replace("menu_", "")
                if pure_id in m_uuid or f"dynamic.{pure_id}" in display_name:
                    return (idx, 1, display_name)
            return (999, 2, display_name)
 
        sorted_display_names = sorted(list(menu_mapping.keys()), key=get_sort_key)
 
        dialog_title = win._i18n.text("sidebar.item.add") or "+ Neues Item"
        prompt_target = win._i18n.text("dialog.item.select.target") or "Ziel-Menü wählen:"
        prompt_de = win._i18n.text("dialog.item.add.de_prompt") or "Deutscher Name des neuen Items:"
        prompt_en = win._i18n.text("dialog.item.add.en_prompt") or "Englischer Name des neuen Items:"
        prompt_type = win._i18n.text("dialog.item.add.type_prompt") or "Typ bestimmen:"
 
        type_action_str = win._i18n.text("dialog.item.add.type_action") or "Aktion (Klickbar)"
        type_sub_str = win._i18n.text("dialog.item.add.type_submenu") or "Submenü (Verschachtelt)"
 
        target_display, ok = QInputDialog.getItem(win, dialog_title, prompt_target, sorted_display_names, 0, False)
        if not ok or not target_display: 
            return
        target_menu_uuid = menu_mapping[target_display]
 
        de_name = ""; en_name = ""
        current_gui_lang = getattr(win._i18n, "_current_lang", "de")
 
        if current_gui_lang == "en":
            en_input, ok1 = QInputDialog.getText(win, dialog_title, prompt_en)
            if not ok1 or not en_input.strip(): return
            en_name = en_input.strip()
            de_input, ok2 = QInputDialog.getText(win, dialog_title, prompt_de, text=en_name)
            if not ok2 or not de_input.strip(): return
            de_name = de_input.strip()
        else:
            de_input, ok1 = QInputDialog.getText(win, dialog_title, prompt_de)
            if not ok1 or not de_input.strip(): return
            de_name = de_input.strip()
            en_input, ok2 = QInputDialog.getText(win, dialog_title, prompt_en, text=de_name)
            if not ok2 or not en_input.strip(): return
            en_name = en_input.strip()
 
        art, ok3 = QInputDialog.getItem(win, dialog_title, prompt_type, [type_action_str, type_sub_str], 0, False)
        if not ok3: 
            return
 
        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()
 
        clean_name = de_name.lower().replace(' ', '_')
        item_id = f"dynamic.{target_menu_uuid.replace('menu_', '')}.{clean_name}"
        item_type = "submenu" if art == type_sub_str else "action"
 
        win._i18n.update_or_append_key(key=item_id, de_text=de_name, en_text=en_name)
        new_item = {"type": item_type, "id": item_id, "items": [] if item_type == "submenu" else None}
        if item_type == "action":
            new_item["command_class"] = "DynamischesTestFeatureCommand"
 
        def append_recursive(menu_dict, target_id, item_to_append):
            if target_id in menu_dict:
                menu_dict[target_id].setdefault("items", []).append(item_to_append)
                return True
            for key, data in menu_dict.items():
                for item in data.get("items", []):
                    if item.get("type") == "submenu" and item.get("id") == target_id:
                        item.setdefault("items", []).append(item_to_append)
                        return True
                    elif item.get("type") == "submenu":
                        if append_recursive({item["id"]: {"items": item.get("items", [])}}, target_id, item_to_append):
                            return True
            return False
 
        append_recursive(cfg.UI_SCHEMA["menu_structure"], target_menu_uuid, new_item)
        win.setup_ui()
        MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_remove_menu_item(win):
        """Löscht ein Item aus seiner exakten Kaskadenebene."""
        items_mapping = MenuDesigner._discover_all_items_nested(win)
        if not items_mapping: 
            return
 
        specific_title = win._i18n.text("sidebar.item.delete") or "- Item löschen"
        chosen_tuple = MenuDesigner._show_generic_selection_dialog(win, "item", items_mapping, custom_title=specific_title)
        if not chosen_tuple: 
            return
 
        items_list, item_obj = chosen_tuple
        confirm_title = "Löschen bestätigen" if win._i18n._current_lang == "de" else "Confirm Delete"
        confirm_msg = f"Möchten du das Element '{win._i18n.text(item_obj['id'])}' wirklich löschen?\n(Untergeordnete Ebenen werden mitgelöscht!)"
        reply = QMessageBox.question(win, confirm_title, confirm_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
 
        if reply == QMessageBox.StandardButton.Yes:
            if "ui_state_manager" in win._services:
                win._services["ui_state_manager"].save_checkpoint()
            items_list.remove(item_obj)
            win.setup_ui()
            MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_rename_menu_item(win):
        """Benennt ein Item auf einer beliebigen Kaskadenebene um."""
        items_mapping = MenuDesigner._discover_all_items_nested(win)
        if not items_mapping: 
            return
 
        specific_title = win._i18n.text("sidebar.item.rename") or "✏️ Item umbenennen"
        chosen_tuple = MenuDesigner._show_generic_selection_dialog(win, "item", items_mapping, custom_title=specific_title)
        if not chosen_tuple: 
            return
 
        _, item_obj = chosen_tuple
        item_id = item_obj["id"]
 
        translations = getattr(win._i18n, "_translations", {})
        current_de = translations.get("de", {}).get(item_id, "")
        current_en = translations.get("en", {}).get(item_id, "")
 
        if not current_de and "de" in translations:
            current_de = translations["de"].get(item_id, "")
        if not current_en and "en" in translations:
            current_en = translations["en"].get(item_id, "")
 
        if not current_de and win._i18n._current_lang == "de":
            current_de = win._i18n.text(item_id)
        if not current_en and win._i18n._current_lang == "en":
            current_en = win._i18n.text(item_id)
 
        prompt_de = win._i18n.text("dialog.item.rename.de_prompt") or "Neuen DEUTSCHEN Namen eingeben:"
        prompt_en = win._i18n.text("dialog.item.rename.en_prompt") or "Enter new ENGLISH name:"
 
        if win._i18n._current_lang == "en":
            neuer_en, ok1 = QInputDialog.getText(win, specific_title, prompt_en, text=current_en)
            if not ok1 or not neuer_en.strip(): return
            neuer_de, ok2 = QInputDialog.getText(win, specific_title, prompt_de, text=current_de or neuer_en.strip())
            if not ok2 or not neuer_de.strip(): return
        else:
            neuer_de, ok1 = QInputDialog.getText(win, specific_title, prompt_de, text=current_de)
            if not ok1 or not neuer_de.strip(): return
            neuer_en, ok2 = QInputDialog.getText(win, specific_title, prompt_en, text=current_en or neuer_de.strip())
            if not ok2 or not neuer_en.strip(): return
 
        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()
 
        win._i18n.update_or_append_key(key=item_id, de_text=neuer_de.strip(), en_text=neuer_en.strip())
        win.setup_ui()
        MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_move_menu_item(win, direction: int):
        """Verschiebt ein Item innerhalb seiner exakten Kaskadenebene."""
        items_mapping = MenuDesigner._discover_all_items_nested(win)
        if not items_mapping: 
            return
 
        if direction == -1:
            specific_title = win._i18n.text("sidebar.item.move_up") or "🔼 Nach oben"
        else:
            specific_title = win._i18n.text("sidebar.item.move_down") or "🔽 Nach unten"
 
        chosen_tuple = MenuDesigner._show_generic_selection_dialog(win, "item", items_mapping, custom_title=specific_title)
        if not chosen_tuple: 
            return
 
        items_list, item_obj = chosen_tuple
        idx = items_list.index(item_obj)
        new_idx = idx + direction
 
        if 0 <= new_idx < len(items_list):
            if "ui_state_manager" in win._services:
                win._services["ui_state_manager"].save_checkpoint()
 
            items_list[idx], items_list[new_idx] = items_list[new_idx], items_list[idx]
            win.setup_ui()
            MenuDesigner._save_schema_to_persistence(win)
    
    @staticmethod
    def _live_assign_macro(win):
        """Weist klickbaren Schaltflächen eServices oder Benutzer-Makros zu.
        Wurde zu Sidebar/DeveloperTools verschoben, da Entwicklerthema"""
        actions_mapping = MenuDesigner._discover_all_items_nested(win, filter_type="action")
        if not actions_mapping: 
            return
 
        specific_title = win._i18n.text("sidebar.item.assign") or "🔗 Befehl zuordnen"
        chosen_tuple = MenuDesigner._show_generic_selection_dialog(win, "item", actions_mapping, custom_title=specific_title)
        if not chosen_tuple: 
            return
 
        items_list, item_obj = chosen_tuple
        selected_item_id = item_obj["id"]
 
        wysiwyg_display_name = selected_item_id
        for display_key, tuple_val in actions_mapping.items():
            if tuple_val == chosen_tuple:
                wysiwyg_display_name = display_key
                break
 
        import os
        import importlib
        macros = []
 
        project_base = getattr(cfg, "PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        user_folder_name = getattr(cfg, "USER_COMMANDS_FOLDER", "commands_user")
        user_package_name = getattr(cfg, "USER_COMMANDS_PACKAGE", f"business.{user_folder_name}")
        user_cmd_dir = os.path.join(project_base, "business", user_folder_name)
 
        if os.path.exists(user_cmd_dir):
            for filename in os.listdir(user_cmd_dir):
                if filename.startswith("cmd_") and filename.endswith(".py"):
                    module_name = filename[:-3]
                    try:
                        mod = importlib.import_module(f"{user_package_name}.{module_name}")
                        for attr in dir(mod):
                            if attr.endswith("Command") and attr != "BaseCommand":
                                macros.append(f"{user_package_name}.{module_name}.{attr}")
                    except Exception as err:
                        print(f"Fehler beim Laden des User-Befehls {module_name}: {err}")
 
        reg_label = " [Externer eService registrieren...]" if win._i18n._current_lang == "de" else " [Register external eService...]"
        macros.append(reg_label)
        macro_label = f"Befehl zuweisen an '{win._i18n.text(selected_item_id)}':"
 
        gewaehltes_macro, ok2 = QInputDialog.getItem(win, specific_title, macro_label, macros, 0, False)
        if ok2 and gewaehltes_macro:
            if "ui_state_manager" in win._services:
                win._services["ui_state_manager"].save_checkpoint()
 
            if gewaehltes_macro == reg_label:
                item_obj["command_class"] = "ExternalServiceAdapter"
                item_obj["external_url"] = "https://example.org"
                msg_title = "eService registriert" if win._i18n._current_lang == "de" else "eService Registered"
                msg_text = f"Der externe eService wurde der Aktion\n'{wysiwyg_display_name}'\nerfolgreich zugewiesen."
            else:
                item_obj["command_class"] = gewaehltes_macro
                class_name = gewaehltes_macro.split(".")[-1]
                msg_title = "Befehl zugeordnet" if win._i18n._current_lang == "de" else "Command Assigned"
                msg_text = f"Das Benutzer-Makro '{class_name}' wurde der Aktion\n'{wysiwyg_display_name}'\nerfolgreich zugeordnet."
 
            win.setup_ui()
            MenuDesigner._save_schema_to_persistence(win)
            win.statusBar().showMessage(msg_text.replace("\n", " "), 4000)
            QMessageBox.information(win, msg_title, msg_text)


    # =========================================================================
    # OPERATIVE LOGIK MIT SCHUTZSCHILDEN (REGISTERKARTEN / TABS)
    # =========================================================================

    
    @staticmethod
    def _live_add_new_tab(win):
        """Erstellt ein neues Forschungs-Register als völlig blanke Fläche. 
        Die Abfragereihenfolge passt sich dynamisch der aktiven Systemsprache an."""
        import uuid
        from PyQt6.QtWidgets import QInputDialog
        import infrastructure.cfg as cfg

        title_prompt = win._i18n.text("sidebar.tab.add") or "Neues Register"
        current_lang = getattr(win._i18n, "_current_lang", "de")
        
        # Initialisierung der Textvariablen (Nur noch Reiter-Namen erforderlich)
        lbl_de = ""
        lbl_en = ""

        # =====================================================================
        # SPRACHADAPTIVE ABFRAGE: Reihenfolge passt sich der aktiven UI-Sprache an
        # =====================================================================
        if current_lang == "en":
            # 1. ENGLISCH ALS REITER-BASIS
            lbl_en, ok1 = QInputDialog.getText(win, title_prompt, "TAB NAME (ENGLISH):")
            if not ok1 or not lbl_en.strip(): return

            # DEUTSCH ALS ERGÄNZUNG (mit englischem Text als Vorschlag)
            lbl_de, ok2 = QInputDialog.getText(win, title_prompt, "REITER-NAME (DEUTSCH):", text=lbl_en.strip())
            if not ok2 or not lbl_de.strip(): return
        else:
            # 1. DEUTSCH ALS REITER-BASIS
            lbl_de, ok1 = QInputDialog.getText(win, title_prompt, "REITER-NAME (DEUTSCH):")
            if not ok1 or not lbl_de.strip(): return

            # ENGLISCH ALS ERGÄNZUNG (mit deutschem Text als Vorschlag)
            lbl_en, ok2 = QInputDialog.getText(win, title_prompt, "TAB NAME (ENGLISH):", text=lbl_de.strip())
            if not ok2 or not lbl_en.strip(): return

        # =====================================================================
        # ARCHITEKTUR-ABSCHLUSS (UUID-Generierung & Blanke Datenstruktur)
        # =====================================================================
        tab_uuid = uuid.uuid4().hex[:8]
        tab_id = f"tab.custom_{tab_uuid}"
        key_label = f"tabs.custom.{tab_uuid}.label"

        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()

        # Sauberes Eintragen des Reiter-Namens in de.json und en.json
        win._i18n.update_or_append_key(key=key_label, de_text=lbl_de.strip(), en_text=lbl_en.strip())

        # Hier wird die neue Konfiguration gebaut:
        # 'elements' ist eine leere Liste [], damit die Fläche absolut blank startet!
        new_tab_config = {
            "id": tab_id,
            "i18n_key": key_label,
            "layout_type": "form",
            "elements": []  # <-- Hier alle alten Platzhalter-Inhalte gelöscht!
        }

        if "tab_structure" not in cfg.UI_SCHEMA:
            cfg.UI_SCHEMA["tab_structure"] = []

        cfg.UI_SCHEMA["tab_structure"].append(new_tab_config)

        # Rendern im Hauptfenster anstoßen
        win._build_tabs(cfg.UI_SCHEMA.get("tab_structure", []))
        win.setup_ui()

        if hasattr(win, "_tabs") and win._tabs.count() > 1:
            win._tabs.setCurrentIndex(win._tabs.count() - 2)

        MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_remove_tab(win):
        """Löscht das aktuell ausgewählte Register unter Einhaltung des Schutzschilds."""
        from PyQt6.QtWidgets import QMessageBox
        import infrastructure.cfg as cfg
        if not hasattr(win, "_tabs"): return
        current_idx = win._tabs.currentIndex()
        
        # Schutzschild: Index 0 (Willkommen) und der Plus-Tab am Ende dürfen nie gelöscht werden
        if current_idx == 0:
            # TIPP für später: "Schutzschild" und den Warntext könnte man hier analog auch über win._i18n übersetzen!
            QMessageBox.warning(win, "Schutzschild", "Das Willkommens-Register ist systemkritisch und geschützt!")
            return
        if current_idx >= win._tabs.count() - 1:
            return

        # --- NEU: Wir holen uns den exakten Anzeigetext des aktuellen Registers aus der GUI ---
        tab_title = win._tabs.tabText(current_idx)

        tab_widget = win._tabs.widget(current_idx)
        tab_id = getattr(tab_widget, "tab_id", None)

        # Sicherheitsabfrage vor dem Löschen (Vollständig bilinguale JIT-Abfrage)
        dialog_title = win._i18n.text("sidebar.tab.delete") or "Register löschen"
        
        # 1. Wir holen den Rohtext aus der JSON-Datei (der den Platzhalter {name} enthält)
        raw_confirm_message = win._i18n.text("dialog.tab.delete.confirm") or "Möchten Sie das Register \"{name}\" wirklich löschen?"
        
        # 2. Dynamische Erweiterbarkeit: Wir ersetzen {name} mit dem echten Registertitel
        # Falls in der JSON kein {name} steht (z.B. alter Text), fängt das try-except einen Absturz sicher ab
        try:
            confirm_message = raw_confirm_message.format(name=tab_title)
        except (KeyError, ValueError):
            confirm_message = raw_confirm_message

        if QMessageBox.question(win, dialog_title, confirm_message,
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()

        # Aus der Schema-Konfiguration entfernen
        cfg.UI_SCHEMA["tab_structure"] = [t for t in cfg.UI_SCHEMA.get("tab_structure", []) if t["id"] != tab_id]
        
        # --- BRÜCKE: Zeichnet die verbleibenden Tabs physisch neu ---
        win._build_tabs(cfg.UI_SCHEMA.get("tab_structure", []))
        
        win.setup_ui()
        win._tabs.setCurrentIndex(max(0, current_idx - 1))
        MenuDesigner._save_schema_to_persistence(win)

    @staticmethod
    def _live_rename_tab(win):
        """Benennt das aktive Register um (Ausschließliche Anpassung des Reiter-Namens)."""
        from PyQt6.QtWidgets import QInputDialog, QMessageBox, QLabel
        import infrastructure.cfg as cfg
        if not hasattr(win, "_tabs"): return
        current_idx = win._tabs.currentIndex()
        
        # Schutzschild: Willkommens-Tab (Index 0) und das "+"-Tab (letzter Index) abfangen
        if current_idx == 0 or current_idx >= win._tabs.count() - 1:
            QMessageBox.warning(win, "Schutzschild", "Dieses Register kann nicht umbenannt werden.")
            return

        tab_widget = win._tabs.widget(current_idx)
        tab_id = getattr(tab_widget, "tab_id", None)
        
        # Passende Konfiguration im Schema suchen
        tab_conf = next((t for t in cfg.UI_SCHEMA.get("tab_structure", []) if t["id"] == tab_id), None)
        if not tab_conf: return

        specific_title = win._i18n.text("sidebar.tab.rename") or "Register umbenennen"
        
        # Ermittle ausschließlich den Sprachschlüssel für den Reiter-Namen
        key_label = tab_conf["i18n_key"]
        
        # Alten Text aus I18N holen für den Standardwert im Prompt-Feld
        old_label_de = win._i18n.text(key_label)
        
        # =====================================================================
        # DIE 2 DIALOGE (Exakte Spiegelung der neuen Erstellungs-Logik)
        # =====================================================================
        neuer_lbl_de, ok1 = QInputDialog.getText(win, specific_title, "REITER-NAME (DEUTSCH):", text=old_label_de)
        if not ok1 or not neuer_lbl_de.strip(): return
        
        neuer_lbl_en, ok2 = QInputDialog.getText(win, specific_title, "TAB NAME (ENGLISH):", text=neuer_lbl_de.strip())
        if not ok2 or not neuer_lbl_en.strip(): return

        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()

        # Synchron in de.json / en.json überschreiben
        win._i18n.update_or_append_key(key=key_label, de_text=neuer_lbl_de.strip(), en_text=neuer_lbl_en.strip())
        
        # =====================================================================
        # WYSIWYG LIVE-UPDATE IM SICHTBAREN FENSTER (Sicherer Austausch)
        # =====================================================================
        # Zwingt den Reiter-Knopf ganz oben, sich sofort umzubenennen
        win._tabs.setTabText(current_idx, win._i18n.text(key_label))
        
        # Alle internen RAM-Sprachschlüssel fliegend aktualisieren
        win._i18n.translate_all()
        
        # Physischer Neuaufbau der Tab-Inhalte über deine bestehende Brücke
        if hasattr(win, "_build_tabs"):
            win._build_tabs(cfg.UI_SCHEMA.get("tab_structure", []))
            win._tabs.setCurrentIndex(current_idx)

        # Schema dauerhaft persistent auf die Festplatte wegsichern
        MenuDesigner._save_schema_to_persistence(win)
        
        # Bestätigung in der Statuszeile anzeigen
        win.statusBar().showMessage(f"Register '{neuer_lbl_de.strip()}' erfolgreich umbenannt.", 3000)

    
    @staticmethod
    def _live_move_tab(win, direction):
        """Verschiebt das aktive Register nach links (-1) oder rechts (+1) innerhalb des Schemas."""
        import infrastructure.cfg as cfg
        if not hasattr(win, "_tabs"): return
        current_idx = win._tabs.currentIndex()
        
        # Schutzschild: Willkommen (0) und Plus-Tab blockieren
        if current_idx == 0 or current_idx >= win._tabs.count() - 1: return
        
        target_idx = current_idx + direction
        # Grenzen prüfen (Darf nicht auf Index 0 und nicht auf/über den Plus-Tab geschoben werden)
        if target_idx <= 0 or target_idx >= win._tabs.count() - 1: return

        tab_widget = win._tabs.widget(current_idx)
        tab_id = getattr(tab_widget, "tab_id", None)

        struct = cfg.UI_SCHEMA.get("tab_structure", [])
        # Finde Index im Konfigurations-Array (Willkommen ist dort meistens Element 0)
        conf_idx = next((i for i, t in enumerate(struct) if t["id"] == tab_id), None)
        if conf_idx is None: return
        
        target_conf_idx = conf_idx + direction
        if target_conf_idx <= 0 or target_conf_idx >= len(struct): return

        if "ui_state_manager" in win._services:
            win._services["ui_state_manager"].save_checkpoint()

        # Swap im Konfigurations-Array
        struct[conf_idx], struct[target_conf_idx] = struct[target_conf_idx], struct[conf_idx]
        
        # --- BRÜCKE: Zeichnet die Tabs in der neuen Reihenfolge neu ---
        win._build_tabs(cfg.UI_SCHEMA.get("tab_structure", []))
        
        win.setup_ui()
        # Fokus auf verschobenem Tab halten
        win._tabs.setCurrentIndex(target_idx)
        MenuDesigner._save_schema_to_persistence(win)


    # -------------------------------------------------------------------------
    # PERSISTENZ-BRÜCKE (DAL)
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _save_schema_to_persistence(win):
        """
        Sichert das gesamte UI-Schema permanent auf die Festplatte.
        Korrigiert, um die Registerkarten (tab_structure) lückenlos mitzuspeichern.
        """
        import infrastructure.cfg as cfg
        import json
        import os

        # Wir bestimmen den exakten Pfad zur dynamic_menu.json
        file_path = getattr(cfg, "JSON_MENU_FILE", "json_storage/dynamic_menu.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            # Wir schnüren das VOLLSTÄNDIGE Paket inklusive deiner Registerkarten!
            payload = {
                "menu_structure": cfg.UI_SCHEMA.get("menu_structure", {}),
                "menu_order": cfg.UI_SCHEMA.get("menu_order", []),
                "tab_structure": cfg.UI_SCHEMA.get("tab_structure", []),  # <-- DAS RETTET DIE TABS!
                "supported_languages": cfg.APP_CONFIG.get("supported_languages", ["de", "en"]),
                "available_languages": cfg.AVAILABLE_LANGUAGES
            }

            # Direkter, unzerbrechlicher Schreibvorgang auf die Festplatte
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
                
            print("[SYSTEM] UI-Schema inklusive Registerkarten erfolgreich persistent gespeichert.")

        except Exception as e:
            print(f"❌ Persistenz-Fehler beim Speichern des UI-Schemas: {e}")


    # -------------------------------------------------------------------------
    # SYNCHRONE AUSWAHLLOGIK (HAUPTMENÜ)
    # -------------------------------------------------------------------------
    @staticmethod
    def _select_main_menu_dialog(win, action_type="select"):
        """Kapselt die Hauptmenü-Auswahl. Garantiert JIT die visuelle Reihenfolge."""
        order = cfg.UI_SCHEMA.get("menu_order", [])
        raw_keys = list(cfg.UI_SCHEMA["menu_structure"].keys())
        if not order:
            order = raw_keys
            cfg.UI_SCHEMA["menu_order"] = order
        for m_key in raw_keys:
            if m_key not in order:
                order.append(m_key)
        menu_uuids = [k for k in order if k in raw_keys]
        if not menu_uuids:
            return None
        display_names = []
        uuid_mapping = {}
        for m_uuid in menu_uuids:
            i18n_key = cfg.UI_SCHEMA["menu_structure"][m_uuid].get("i18n_key", f"menu.{m_uuid}")
            name = win._i18n.text(i18n_key)
            display_str = f"{name} ({m_uuid[:8]})"
            display_names.append(display_str)
            uuid_mapping[display_str] = m_uuid
        if action_type == "delete":
            specific_title = win._i18n.text("sidebar.menu.delete") or "- Hauptmenü löschen"
        elif action_type == "rename":
            specific_title = win._i18n.text("sidebar.menu.rename") or "✏️ Hauptmenü umbenennen"
        elif action_type == "move_left":
            specific_title = win._i18n.text("sidebar.menu.move_left") or "⬅️ Nach links"
        elif action_type == "move_right":
            specific_title = win._i18n.text("sidebar.menu.move_right") or "➡️ Nach rechts"
        else:
            specific_title = win._i18n.text("sidebar.menu.group") or "HAUPTMENÜ"
        return MenuDesigner._show_generic_selection_dialog(win, "menu", uuid_mapping, custom_title=specific_title)
