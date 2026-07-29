# -*- coding: utf-8 -*-
"""Presentation Layer: Generische Widget-Fabrik mit Editor-Sprung und Größen-Begrenzung"""

import os
import subprocess
from PyQt6.QtWidgets import (QLabel, QPushButton, QLineEdit, QTextEdit, 
                             QComboBox, QCheckBox, QRadioButton, QGroupBox, QVBoxLayout)
import infrastructure.cfg as cfg

class WidgetFactory:
    """Erzeugt und stylet UI-Elemente rein deklarativ anhand des Schemas."""
    
    @staticmethod
    def create_widget(elem_config: dict, services: dict, element_registry: dict):
        """Fabrik-Methode: Baut das passende Widget und wendet das rahmenlose Styling an."""
        i18n = services["i18n"]
        elem_type = elem_config["type"]
        elem_id = elem_config["id"]
        widget = None
        
        if elem_type == "label":
            widget = QLabel()
            i18n.register(widget, "headline", elem_config["i18n_key"])
            
        elif elem_type == "text_viewer":
            widget = QTextEdit()
            widget.setReadOnly(True)
            i18n.register(widget, "placeholder", elem_config["placeholder_i18n"])
            widget.setStyleSheet("border: 1px solid #ced4da; border-radius: 4px; background-color: #f8f9fa; color: #495057;")
            element_registry[elem_id] = widget
            
        elif elem_type == "input_line":
            widget = QLineEdit()
            i18n.register(widget, "placeholder", elem_config["placeholder_i18n"])
            widget.setStyleSheet("border: 1px solid #ced4da; border-radius: 4px; padding: 6px; background-color: #ffffff;")
            element_registry[elem_id] = widget
            
        elif elem_type == "input_text":
            widget = QTextEdit()
            i18n.register(widget, "placeholder", elem_config["placeholder_i18n"])
            widget.setStyleSheet("border: 1px solid #ced4da; border-radius: 4px; padding: 6px; background-color: #ffffff;")
            element_registry[elem_id] = widget
            
        elif elem_type == "button":
            widget = QPushButton()
            i18n.register(widget, "button", elem_config["i18n_key"])
            widget.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px; padding: 7px; font-weight: bold;")
            
            if "macro_file" in elem_config and "macro_event" in elem_config:
                # Signal-Schutz: Alte Verbindungen kappen, um Blockaden zu verhindern
                try: widget.clicked.disconnect()
                except Exception: pass
                widget.clicked.connect(
                    lambda checked: WidgetFactory._trigger_live_macro(services, elem_config, checked)
                )
            element_registry[elem_id] = widget

        elif elem_type == "combobox":
            widget = QComboBox()
            widget.setStyleSheet("border: 1px solid #ced4da; border-radius: 4px; padding: 5px; background-color: #ffffff;")
            # Falls ein Platzhalter-Key im Schema definiert ist, als Typ "placeholder" registrieren
            if "placeholder_i18n" in elem_config:
                i18n.register(widget, "placeholder", elem_config["placeholder_i18n"])
            else:
                widget.addItem("Auswahl 1")
                widget.addItem("Auswahl 2")
            
            if "macro_file" in elem_config and "macro_event" in elem_config:
                try: widget.currentTextChanged.disconnect()
                except Exception: pass
                widget.currentTextChanged.connect(
                    lambda text: WidgetFactory._trigger_live_macro(services, elem_config, text)
                )
            element_registry[elem_id] = widget
            
        elif elem_type == "checkbox":
            widget = QCheckBox()
            # Registrierung als "checkbox"-Typ für dedizierte Text-Zuweisung
            i18n.register(widget, "checkbox", elem_config["i18n_key"])
            widget.setStyleSheet("background-color: transparent; padding: 4px;")
            
            if "macro_file" in elem_config and "macro_event" in elem_config:
                try: widget.toggled.disconnect()
                except Exception: pass
                widget.toggled.connect(
                    lambda is_checked: WidgetFactory._trigger_live_macro(services, elem_config, is_checked)
                )
            element_registry[elem_id] = widget
            
        elif elem_type == "radiobutton":
            widget = QRadioButton()
            # Registrierung als "radiobutton"-Typ
            i18n.register(widget, "radiobutton", elem_config["i18n_key"])
            widget.setStyleSheet("background-color: transparent; padding: 4px;")
            
            if "macro_file" in elem_config and "macro_event" in elem_config:
                try: widget.toggled.disconnect()
                except Exception: pass
                widget.toggled.connect(
                    lambda is_checked: WidgetFactory._trigger_live_macro(services, elem_config, is_checked)
                )
            element_registry[elem_id] = widget
            
        elif elem_type == "groupbox":
            widget = QGroupBox()
            # GroupBox benötigt ".setTitle()", daher als Typ "groupbox" registrieren
            i18n.register(widget, "groupbox", elem_config["i18n_key"])
            group_layout = QVBoxLayout(widget)
            group_layout.setContentsMargins(8, 16, 8, 8)
            widget.setStyleSheet("QGroupBox { border: 1px solid #ced4da; border-radius: 4px; margin-top: 6px; font-weight: bold; }")
            element_registry[elem_id] = widget

        
        # =====================================================================
        # UNIVERSAL-GRÖSSEN- UND POSITIONSSTEUERUNG FÜR ALLE ELEMENTE
        # =====================================================================
        if widget and "width" in elem_config and "height" in elem_config:
            widget.setFixedSize(int(elem_config["width"]), int(elem_config["height"]))
        elif widget and "width" in elem_config:
            widget.setFixedWidth(int(elem_config["width"]))
            
        if widget and "x" in elem_config and "y" in elem_config:
            widget.move(int(elem_config["x"]), int(elem_config["y"]))

        # ONCE-ONLY: AUTOMATISCHER RECHTSKLICK-SCHUTZ FÜR ALLE ELEMENTE
        if widget and "macro_file" in elem_config and "macro_event" in elem_config:
            WidgetFactory._attach_developer_context_menu(widget, services, elem_config)
            
        return widget

    @staticmethod
    def _trigger_live_macro(services: dict, elem_config: dict, event_data):
        """Zentrale Brücke, die Events an das Tab-Sammel-Makro weiterleitet und die IDE öffnet."""
        import importlib
        from PyQt6.QtWidgets import QApplication
        
        module_path = elem_config.get("macro_file")
        event_method_name = elem_config.get("macro_event")
        
        if not module_path or not event_method_name:
            return
            
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)
            file_absolute_path = getattr(module, "__file__", None)
            
            for attr_name in dir(module):
                if attr_name.startswith("TabControl_") or attr_name.endswith("Command"):
                    cls = getattr(module, attr_name)
                    main_win = None
                    for w in QApplication.topLevelWidgets():
                        if w.inherits("QMainWindow"):
                            main_win = w
                            break
                            
                    if main_win:
                        instance = cls(main_win)
                        if hasattr(instance, event_method_name):
                            method = getattr(instance, event_method_name)
                            method(event_data)
                            
                            if file_absolute_path and os.path.exists(file_absolute_path):
                                line_number = 1
                                try:
                                    with open(file_absolute_path, "r", encoding="utf-8") as f:
                                        for idx, line in enumerate(f, 1):
                                            if f"def {event_method_name}" in line:
                                                line_number = idx
                                                break
                                except Exception:
                                    pass
                                    
                                # OPTIONALER EDITOR-SPRUNG MIT OK/CANCEL BUTTONS
                                from PyQt6.QtWidgets import QMessageBox
                                i18n = services.get("i18n")
                                lang = getattr(i18n, "_current_lang", "de")
                                
                                btn_ok_text = i18n.text("ide.sonde.btn_edit") if i18n else ("Code bearbeiten" if lang == "de" else "Edit Code")
                                btn_cancel_text = i18n.text("ide.sonde.btn_close") if i18n else ("Schließen" if lang == "de" else "Close")
                                
                                msg_box = QMessageBox(main_win)
                                msg_box.setWindowTitle(i18n.text("ide.sonde.title") or "ClioGraph IDE")
                                msg_box.setText(i18n.text("ide.sonde.question") or ("Möchten Sie das Makro in VS Code bearbeiten?" if lang == "de" else "Do you want to edit the macro in VS Code?"))
                                msg_box.setIcon(QMessageBox.Icon.Question)
                                
                                edit_button = msg_box.addButton(btn_ok_text, QMessageBox.ButtonRole.ActionRole)
                                close_button = msg_box.addButton(btn_cancel_text, QMessageBox.ButtonRole.RejectRole)
                                msg_box.exec()
                                
                                if msg_box.clickedButton() == edit_button:
                                    try:
                                        subprocess.Popen([cfg.EXTERNAL_EDITOR_COMMAND, "-g", f"{file_absolute_path}:{line_number}"], shell=True)
                                    except Exception:
                                        pass
                        break
        except Exception as e:
            print(f" [IDE-LIVE-MACRO] Fehler: {e}")

    @staticmethod
    def _attach_developer_context_menu(widget, services: dict, elem_config: dict):
        """Kapselt das bilinguale IDE-Kontextmenü für JEDES Widget mit sauberer Speicher-Trennung."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QAction
        from PyQt6.QtWidgets import QMenu, QDialog, QLabel, QSpinBox, QPushButton, QFormLayout, QApplication
        import infrastructure.cfg as cfg

        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        def get_main_window():
            if services and "main_window" in services:
                return services["main_window"]
            for w in QApplication.topLevelWidgets():
                if w.inherits("QMainWindow"):
                    return w
            return None

        def refresh_ui(main_win):
            if not main_win:
                return
            from PyQt6.QtWidgets import QApplication, QScrollArea, QWidget
            import infrastructure.cfg as cfg

            persistence = main_win._services.get("menu_persistence")
            if persistence and hasattr(persistence, "save_menus"):
                persistence.save_menus(cfg.UI_SCHEMA)
         
            outer_widget = main_win._tabs.currentWidget()
            if not outer_widget:
                return

            if isinstance(outer_widget, QScrollArea):
                current_tab = outer_widget.widget()
            else:
                current_tab = outer_widget

            if current_tab:
                if hasattr(current_tab, "canvas_widget") and current_tab.canvas_widget:
                    for child in current_tab.canvas_widget.findChildren(QWidget):
                        child.setParent(None)
                        child.deleteLater()
                    current_tab.canvas_widget.setMinimumSize(0, 0)

                if current_tab.layout():
                    layout = current_tab.layout()
                    for i in reversed(range(layout.count())):
                        item = layout.itemAt(i)
                        if item and item.widget():
                            w = item.widget()
                            layout.removeWidget(w)
                            w.setParent(None)
                            w.deleteLater()
         
                if hasattr(current_tab, "element_registry"):
                    current_tab.element_registry.clear()
         
                t_id = getattr(current_tab, "tab_id", "unknown")
                tab_schema = next((t for t in cfg.UI_SCHEMA.get("tab_structure", []) if t.get("id") == t_id), {})
                elements_list = tab_schema.get("elements", [])
         
                if hasattr(current_tab, "_build_tab_geometry"):
                    current_tab._build_tab_geometry(elements_list)
                elif hasattr(main_win, "build_dynamic_tabs"):
                    main_win.build_dynamic_tabs()
         
            i18n = main_win._services.get("i18n")
            if i18n:
                i18n.translate_all()

            if current_tab and hasattr(current_tab, "canvas_widget") and current_tab.canvas_widget:
                for child in current_tab.canvas_widget.findChildren(QWidget):
                    child.show()
                    child.raise_()
         
            QApplication.processEvents()
            if main_win:
                main_win.update()

        def show_menu(pos):
            i18n = services.get("i18n")
            lang = getattr(i18n, "_current_lang", "de")
            main_win = get_main_window()
            
            txt_jump = i18n.text("ide.context.jump_macro") if i18n else ("[IDE] Zum Makro-Code springen" if lang == "de" else "[IDE] Jump to Macro Code")
            txt_prop = i18n.text("ide.context.properties") if i18n else ("[IDE] Größe und Position..." if lang == "de" else "[IDE] Size and Position...")
            txt_up = i18n.text("ide.context.move_up") if i18n else ("[IDE] Nach oben verschieben" if lang == "de" else "[IDE] Move Up")
            txt_down = i18n.text("ide.context.move_down") if i18n else ("[IDE] Nach unten verschieben" if lang == "de" else "[IDE] Move Down")
            txt_ren = "[IDE] Element umbenennen" if lang == "de" else "[IDE] Rename Element"
            txt_del = i18n.text("ide.context.delete") if i18n else ("[IDE] Element löschen" if lang == "de" else "[IDE] Delete Element")

            context_menu = QMenu(main_win or widget)
            
            act_jump = QAction(txt_jump, context_menu)
            act_jump.triggered.connect(lambda: WidgetFactory._trigger_live_macro(services, elem_config, None))
            context_menu.addAction(act_jump)
            context_menu.addSeparator()
            
            act_prop = QAction(txt_prop, context_menu)
            act_prop.triggered.connect(lambda: open_properties_dialog(get_main_window(), services.get("i18n"), elem_config, widget))
            context_menu.addAction(act_prop)
            
            act_up = QAction(txt_up, context_menu)
            act_up.triggered.connect(lambda: move_element(main_win, -1))
            context_menu.addAction(act_up)
            
            act_down = QAction(txt_down, context_menu)
            act_down.triggered.connect(lambda: move_element(main_win, 1))
            context_menu.addAction(act_down)
            
            act_ren = QAction(txt_ren, context_menu)
            act_ren.triggered.connect(lambda: rename_element(main_win))
            context_menu.addAction(act_ren)
            
            context_menu.addSeparator()
            
            act_del = QAction(txt_del, context_menu)
            act_del.triggered.connect(lambda: delete_element(main_win))
            context_menu.addAction(act_del)
            
            context_menu.exec(widget.mapToGlobal(pos))

        def rename_element(main_win):
            from PyQt6.QtWidgets import QInputDialog
            import json
            import os
 
            i18n = services.get("i18n")
            lang = getattr(i18n, "_current_lang", "de")
 
            # Aktuellen Text als Startwert ermitteln
            current_display_text = widget.text() if hasattr(widget, "text") else ""
 
            de_title = "Zweisprachigkeit garantieren" if lang == "de" else "Guarantee Bilingualism"
            de_text, ok_de = QInputDialog.getText(
                main_win, de_title, "Neuen DEUTSCHEN Namen eingeben:", text=current_display_text
            )
            if not (ok_de and de_text.strip()):
                return
 
            en_text, ok_en = QInputDialog.getText(
                main_win, de_title, "Enter new ENGLISH name:", text=de_text.strip()
            )
            if not (ok_en and en_text.strip()):
                return

            # Bestimmen oder Erzeugen des i18n_key für das Element
            i18n_key = elem_config.get("i18n_key")
            if not i18n_key:
                i18n_key = f"dynamic.element.{elem_config.get('id')}"
                elem_config["i18n_key"] = i18n_key

            # Festplatten-Synchronisierung für beide JSONs
            for code, text_value in [("de", de_text.strip()), ("en", en_text.strip())]:
                file_path = os.path.join(cfg.JSON_LOCALES_DIR, f"{code}.json")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            locales_data = json.load(f)
                        
                        locales_data[i18n_key] = text_value
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(locales_data, f, ensure_ascii=False, indent=4)
                    except Exception as e:
                        print(f" Fehler beim Schreiben in {code}.json: {e}")

            # RAM-Cache des Übersetzungsservices direkt aktualisieren
            if i18n and hasattr(i18n, "_data"):
                if "de" in i18n._data: i18n._data["de"][i18n_key] = de_text.strip()
                if "en" in i18n._data: i18n._data["en"][i18n_key] = en_text.strip()
            elif i18n and hasattr(i18n, "_locales"):
                if "de" in i18n._locales: i18n._locales["de"][i18n_key] = de_text.strip()
                if "en" in i18n._locales: i18n._locales["en"][i18n_key] = en_text.strip()

            # WYSIWYG-LÖSUNG (Wie bei Größe & Position): Text direkt auf das Widget prägen
            chosen_text = de_text.strip() if lang == "de" else en_text.strip()
            if hasattr(widget, "setText"):
                widget.setText(chosen_text)

            # Menü-Struktur absichern ohne die Tabs neu aufzubauen
            if main_win:
                persistence = main_win._services.get("menu_persistence")
                if persistence and hasattr(persistence, "save_menus"):
                    persistence.save_menus(cfg.UI_SCHEMA)
                
                if "ui_state_manager" in main_win._services:
                    main_win._services["ui_state_manager"].save_checkpoint()

            # Sofortiges, sauberes Live-Repaint des modifizierten Widgets
            widget.updateGeometry()
            widget.repaint()
            widget.show()
            widget.raise_()
            
            if main_win:
                main_win.update()

        
        def open_properties_dialog(main_win, i18n, elem_config, widget):
            dialog = QDialog(main_win)
            dialog.setWindowTitle(i18n.text("ide.dialog.prop_title") or "Form formatieren")
            layout = QFormLayout(dialog)

            sb_width = QSpinBox()
            sb_width.setRange(40, 2000)
            sb_width.setValue(elem_config.get("width", widget.width()))

            sb_height = QSpinBox()
            sb_height.setRange(20, 2000)
            sb_height.setValue(elem_config.get("height", widget.height()))

            sb_x = QSpinBox()
            sb_x.setRange(0, 4000)
            sb_x.setValue(elem_config.get("x", widget.x()))

            sb_y = QSpinBox()
            sb_y.setRange(0, 4000)
            sb_y.setValue(elem_config.get("y", widget.y()))

            layout.addRow(QLabel(i18n.text("ide.dialog.width") or "Breite (px):"), sb_width)
            layout.addRow(QLabel(i18n.text("ide.dialog.height") or "Höhe (px):"), sb_height)
            layout.addRow(QLabel("X-Koordinate:"), sb_x)
            layout.addRow(QLabel("Y-Koordinate:"), sb_y)

            btn_save = QPushButton(i18n.text("ide.dialog.save") or "Speichern")
            layout.addWidget(btn_save)

            def save_props():
                RASTER = 10
                new_w = round(sb_width.value() / RASTER) * RASTER
                new_h = round(sb_height.value() / RASTER) * RASTER
                new_x = round(sb_x.value() / RASTER) * RASTER
                new_y = round(sb_y.value() / RASTER) * RASTER
                elem_config["width"] = new_w
                elem_config["height"] = new_h
                elem_config["x"] = new_x
                elem_config["y"] = new_y
                if widget:
                    widget.setFixedSize(new_w, new_h)
                    widget.move(new_x, new_y)
                current_tab = main_win._tabs.currentWidget()
                from PyQt6.QtWidgets import QScrollArea
                if isinstance(current_tab, QScrollArea):
                    current_tab = current_tab.widget()
                if current_tab and hasattr(current_tab, "canvas_widget") and current_tab.canvas_widget:
                    needed_w = new_x + new_w + 40
                    needed_h = new_y + new_h + 40
                    current_tab.canvas_widget.setMinimumSize(
                        max(current_tab.canvas_widget.minimumWidth(), needed_w),
                        max(current_tab.canvas_widget.minimumHeight(), needed_h)
                    )
                widget.updateGeometry()
                widget.repaint()
                widget.show()
                widget.raise_()
                try: widget.customContextMenuRequested.disconnect()
                except Exception: pass
                widget.customContextMenuRequested.connect(lambda pos: show_menu(pos))
                persistence = main_win._services.get("menu_persistence")
                if persistence and hasattr(persistence, "save_menus"):
                    import infrastructure.cfg as cfg
                    persistence.save_menus(cfg.UI_SCHEMA)
                dialog.accept()
                if main_win:
                    main_win.update()

            btn_save.clicked.connect(save_props)
            dialog.exec()

        def move_element(main_win, direction):
            SCHRITTWEITE = 15
            neues_y = elem_config.get("y", 0) + (direction * SCHRITTWEITE)
            elem_config["y"] = max(0, neues_y)
            if widget:
                widget.move(int(elem_config.get("x", 0)), int(elem_config["y"]))
                widget.updateGeometry()
                widget.repaint()
            persistence = main_win._services.get("menu_persistence") if main_win else None
            if persistence and hasattr(persistence, "save_menus"):
                persistence.save_menus(cfg.UI_SCHEMA)

        def delete_element(main_win):
            for t_conf in cfg.UI_SCHEMA.get("tab_structure", []):
                elements = t_conf.get("elements", [])
                for i, elem in enumerate(elements):
                    if elem.get("id") == elem_config.get("id"):
                        elements.pop(i)
                        if widget:
                            widget.setParent(None)
                            widget.deleteLater()
                        persistence = main_win._services.get("menu_persistence") if main_win else None
                        if persistence and hasattr(persistence, "save_menus"):
                            persistence.save_menus(cfg.UI_SCHEMA)
                        return

        try: 
            widget.customContextMenuRequested.disconnect()
        except Exception: 
            pass

        widget.customContextMenuRequested.connect(lambda pos: show_menu(pos))
