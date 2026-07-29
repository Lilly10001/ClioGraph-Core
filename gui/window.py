"""Presentation Layer: Generisches Hauptfenster-Gehäuse (MainWindow) mit optimierter Pfeil-Faltung"""
import uuid
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QInputDialog, QSplitter, QWidget, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
import copy 
import infrastructure.cfg as cfg
from .tabs import DynamicTab
from .designer import MenuDesigner
from .sidebar import SidebarController

class MainWindow(QMainWindow):

    """Das vollkommen generische Hauptfenster von ClioGraph mit einklappbarer Sidebar."""      
    def __init__(self, services: dict, ui_schema: dict):
        super().__init__()
        import infrastructure.cfg as cfg  # Sicherstellen, dass cfg importiert ist
        import json
        import os
        
        self._services = services
        self._i18n = services["i18n"]
        self._schema = ui_schema
        self._tab_mapping = []  
        self._btn_toggle_sidebar = None
        self._sidebar_title_label = None
        self._designer_content = None
        self._sidebar_is_collapsed = False
        self.resize(1150, 700)
        
        # =====================================================================
        # DATENFLUSS-REPARATUR: Direktes, lückenloses Laden von der Festplatte
        # =====================================================================
        file_path = getattr(cfg, "DYNAMIC_MENU_PATH", "json_storage/dynamic_menu.json")
        
        # Falls die JSON-Datei existiert, lesen wir das VOLLSTÄNDIGE Live-Schema ein
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    full_schema = json.load(f)
                    
                    cfg.UI_SCHEMA["menu_structure"] = full_schema.get("menu_structure", {})
                    cfg.UI_SCHEMA["menu_order"] = full_schema.get("menu_order", [])
                    # --- KERN-REPARATUR: Register werden nun garantiert persistent geladen! ---
                    cfg.UI_SCHEMA["tab_structure"] = full_schema.get("tab_structure", [])
            except Exception as e:
                print(f"🚨 Fehler beim Laden des Registerschemas aus {file_path}: {e}")
        else:
            # Fallback, falls die Datei noch gar nicht existiert (z. B. nach dem Löschen)
            if ui_schema:
                cfg.UI_SCHEMA["menu_structure"] = ui_schema.get("menu_structure", {})
                cfg.UI_SCHEMA["menu_order"] = ui_schema.get("menu_order", [])
                cfg.UI_SCHEMA["tab_structure"] = ui_schema.get("tab_structure", [])
        
        # =====================================================================
        # VISUELLE IDENTITÄT: Echtes Kleeblatt-Icon (Vernichtet das Windows-Rechteck!)
        # =====================================================================
        self.setWindowIcon(self._generate_clover_icon())

        # 1. ZENTRALER SPLITTER
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter.setHandleWidth(4)
        self._main_splitter.setStyleSheet("QSplitter::handle { background-color: #ced4da; }")
        
        # 2. Modularen Sidebar-Manager für die linke Seite einsetzen (VS-Code Style)
        self.sidebar_manager = SidebarController(self)
        self._main_splitter.addWidget(self.sidebar_manager)

        # 3. Das Tab-Widget für die rechte Seite
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("QTabWidget::pane { border: none; }")
        
        # =====================================================================
        # HIER IST JETZT DER RICHTIGE PLATZ (Das Objekt existiert nun sicher!)
        # =====================================================================
        self._tabs.currentChanged.connect(self._on_tab_changed_check_plus)
        self._main_splitter.addWidget(self._tabs)
        self.setCentralWidget(self._main_splitter)
        
        # Start-Größenverteilung setzen
        self._main_splitter.setSizes([220, 1150 - 220])
        
        # Hellgraue vertikale Abgrenzungsstriche und VS-Style Aktiv-Hervorhebung oben
        self.menuBar().setStyleSheet("""
            QMenuBar {
                background-color: #f0f0f0;  /* Neutraler, hellgrauer Menühintergrund */
                border-bottom: 1px solid #ced4da;
            }
            QMenuBar::item {
                border-right: 1px solid #d3d3d3;
                padding-left: 12px;
                padding-right: 12px;
                padding-top: 6px;
                padding-bottom: 6px;
                background-color: transparent;
            }
            QMenuBar::item:last {
                border-right: none;
            }
            
            /* --- NEU: Wenn man mit der Maus drüberfährt (Hover) --- */
            QMenuBar::item:selected {
                background-color: #e2e8f0;
                color: #000000;
            }
            
            /* --- NEU: Wenn das Hauptmenü angeklickt wurde / offen ist (Aktiv-Zustand) --- */
            QMenuBar::item:pressed {
                background-color: #ffffff;  /* Reines Weiß wie die aktiven Registerkarten */
                color: #1a73e8;            /* Clio-Tech-Blau für die aktive Schrift */
                font-weight: bold;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border-bottom: 1px solid #ffffff; /* Verschmilzt visuell nach unten */
            }
        """)



        # =====================================================================
        # CORE INJEKTION: UI STATE MANAGER FÜR UNDO / REDO ACTIVATION
        # =====================================================================
        from infrastructure.ui_state_manager import UIStateManager
        self._services["ui_state_manager"] = UIStateManager(self._i18n)

        # Triggert nun den UI-Aufbau mit der korrekten Register-Injektion im RAM
        self.setup_ui()

    def setup_ui(self):
        """Baut Menüs, die linke Designer-Sidebar und Tabs strikt nach Schema auf."""
        import infrastructure.cfg as cfg
        self.menuBar().clear()
        
        # 1. Obere Menüs aus der Konfiguration generieren
        self._build_menu_recursive(self.menuBar(), cfg.UI_SCHEMA.get("menu_structure", {}))
        
        # Excel-Style Plus-Schaltfeld ans Ende hängen (sofern Obergrenze nicht erreicht)
        current_menu_count = len(cfg.UI_SCHEMA.get("menu_structure", {}).keys())
        if current_menu_count < cfg.APP_CONFIG.get("max_main_menus", 10):
            plus_action = self.menuBar().addAction("+")
            plus_action.setToolTip("Neues Hauptmenü hinzufügen")
            plus_action.triggered.connect(self.create_new_main_menu)
        
        # 2. Den Designer als Modul in der neuen Icon-Sidebar registrieren (Nur einmalig)
        if not self.sidebar_manager.sidebar_mapping:
            from .designer import MenuDesigner
            from PyQt6.QtWidgets import QWidget
            
            # --- KNOPF 1: SYSTEMDESIGNER (FÜR FORSCHER) ---
            designer_container = QWidget()
            MenuDesigner.inject_designer_sidebar_at(self, designer_container)
            
            self.sidebar_manager.register_sidebar(
                sidebar_id="system_designer",
                icon_text="⚙️",
                widget=designer_container,
                tooltip="System-Designer (Menüs & Register)"
            )
            
            # --- KNOPF 2: ENTWICKLERTOOLS (FÜR ENTWICKLER / HYBRID-IDE) ---
            from .ide_designer import IDEDesigner
            
            self._ide_container = QWidget() # Sicher als Instanz-Variable verankert
            IDEDesigner.inject_ide_sidebar_at(self, self._ide_container)
            
            dev_tooltip = self._i18n.text("sidebar.btn.developer_tool") or "Entwicklertools (VBA & GenAI)"
            
            self.sidebar_manager.register_sidebar(
                sidebar_id="developer_tools",
                icon_text="🧳", # Hier ist das korrekte Koffer-Icon gesetzt!
                widget=self._ide_container, 
                tooltip=dev_tooltip
            )
   

            # Standardmäßig zugeklappt starten
            self.sidebar_manager.content_stack.hide()
            self._main_splitter.setSizes([46, self.width() - 46])
        
        # =====================================================================
        # 3. KERN-REPARATUR: DELEGIERT DAS INTEGRATIVE RENDERN VOLLSTÄNDIG
        # =====================================================================
        # Wir überlassen das saubere Zeichnen komplett der spezialisierten Methode!
        # Das verhindert die doppelte Initiierung des Willkommens-Registers.
        self._build_tabs(cfg.UI_SCHEMA.get("tab_structure", []))
        
        # Falls noch kein aktives Menü gesetzt ist, initialisiere es mit dem ersten dynamischen Eintrag
        # --- SICHERHEITSANKER: Gedächtnis mit der exakten ersten Menü-ID bespielen ---
        if not hasattr(self, "_active_menu_uuid") or not self._active_menu_uuid:
            import infrastructure.cfg as cfg
            order = cfg.UI_SCHEMA.get("menu_order", [])
            dynamic_menus = [k for k in order if k != "file"]
            if dynamic_menus:
                # Wir nehmen die echte, rohe ID-Zeichenkette (z.B. "menu_xyz")
                self._active_menu_uuid = dynamic_menus[0]




        # Erzwingt das sofortige Übersetzen aller registrierten UI-Elemente
        self.refresh_ui_texts()
  
    def _on_tab_changed_check_plus(self, index):
        """Prüft, ob das allerletzte Tab (das '+' Feld) angeklickt wurde, und erzeugt JIT ein neues Register."""
        # 1. SICHERHEITSANKER: Wenn der Index ungültig oder im Minus ist, sofort abbrechen
        if index < 0 or index >= self._tabs.count():
            return
    
        # 2. URSACHEN-KILLER: Beim allerersten Start (Index 0, Willkommen) darf NIEMALS der Dialog kommen!
        if index == 0:
            return
            
        # 3. TEXT-CHECK: Nur wenn das angeklickte Feld wirklich die Plus-Schaltfläche ist
        tab_text = self._tabs.tabText(index).strip()
        if tab_text == "+":
            from .designer import MenuDesigner
    
            # Signale kurz stummschalten, um Endlosschleifen beim Einfügen zu unterbinden
            self._tabs.blockSignals(True)
    
            # Ruft DEINE NEUE sichere Logik im MenuDesigner auf (schreibt direkt in de.json/en.json via UUID)
            MenuDesigner._live_add_new_tab(self)
    
            # Signale sofort wieder freigeben
            self._tabs.blockSignals(False)


    def toggle_sidebar(self):
        """Kollabiert oder expandiert die Sidebar im Splitter, schaltet Sichtbarkeiten um."""
        if not self._sidebar_is_collapsed:
            if self._designer_content: self._designer_content.hide()
            if self._sidebar_title_label: self._sidebar_title_label.hide()
            self._sidebar_container.setFixedWidth(34)
            self._main_splitter.handle(1).setEnabled(False)
            if self._btn_toggle_sidebar: self._btn_toggle_sidebar.setText("▶")
            self._sidebar_is_collapsed = True
        else:
            self._sidebar_container.setMinimumWidth(220)
            self._sidebar_container.setMaximumWidth(16777215)
            self._main_splitter.handle(1).setEnabled(True)
            self._main_splitter.setSizes([220, self.width() - 220])
            if self._designer_content: self._designer_content.show()
            if self._sidebar_title_label: self._sidebar_title_label.show()
            if self._btn_toggle_sidebar: self._btn_toggle_sidebar.setText("◀")
            self._sidebar_is_collapsed = False

    def _build_menu_recursive(self, parent_menu_component, menu_schema: dict):
        """Erlaubt geordnete Generierung der Hauptmenüs nach menu_order."""
        import infrastructure.cfg as cfg
        
        # Wenn wir auf oberster Ebene (MenuBar) sind, nutzen wir unsere menu_order Liste!
        if isinstance(parent_menu_component, type(self.menuBar())):
            order = cfg.UI_SCHEMA.get("menu_order", [])
            if not order:
                order = list(menu_schema.keys())
                cfg.UI_SCHEMA["menu_order"] = order
                
            # Synchronisation: Neue Menüs hinten anhängen
            for m_key in menu_schema.keys():
                if m_key not in order:
                    order.append(m_key)
                    
            for key in order:
                if key not in menu_schema: 
                    continue
                menu_data = menu_schema[key]
                localized_title = self._i18n.text(menu_data.get("i18n_key", f"menu.{key}"))
                
                # Menü erzeugen
                current_menu = parent_menu_component.addMenu(localized_title)
                
                # --- DIE RETTUNG: Sobald das Menü angeklickt wird, im Gedächtnis verankern! ---
                current_menu.aboutToShow.connect(lambda k=key: setattr(self, "_active_menu_uuid", k))
                
                # --- KORREKTUR: Diese Schleife MUSS innerhalb der 'key'-Schleife eingerückt sein! ---
                for item in menu_data.get("items", []):
                    # SCAN-SONDE: Druckt jedes geladene Item ins Terminal
                    print(f"[I18N-DEBUG-SCAN] Item-ID: {item.get('id')} | Command: {item.get('command_class')}")
                    
                    if item["type"] == "separator":
                        current_menu.addSeparator()
                    elif item["type"] == "action":
                        action_title = self._i18n.text(item["id"])
                        action = current_menu.addAction(action_title)
                        
                        cmd_class = item.get("command_class")
                        if cmd_class == "ChangeLanguageCommand":
                            action.triggered.connect(lambda checked: self._change_language_dialog())
                        elif cmd_class == "ExitCommand":
                            action.triggered.connect(lambda checked: self.close())
                        elif cmd_class == "ResetSystemCommand":
                            action.triggered.connect(lambda checked: self._execute_system_reset_direct())
                        elif cmd_class:
                            action.triggered.connect(lambda checked, c=cmd_class: self._dispatch_custom_user_command(c))
                    elif item["type"] == "submenu":
                        sub_item = item.copy()
                        sub_item["i18n_key"] = item.get("id")
                        sub_schema = { item.get("id", "sub"): sub_item }
                        self._build_menu_recursive(current_menu, sub_schema)
                        
        # Für tiefere Kaskadenebenen (Submenüs), die nicht direkt auf der MenuBar liegen
        else:
            for key, menu_data in menu_schema.items():
                localized_title = self._i18n.text(menu_data.get("i18n_key", f"menu.{key}"))
                current_menu = parent_menu_component.addMenu(localized_title)
                
                for item in menu_data.get("items", []):
                    if item["type"] == "separator":
                        current_menu.addSeparator()
                    elif item["type"] == "action":
                        action_title = self._i18n.text(item["id"])
                        action = current_menu.addAction(action_title)
                        cmd_class = item.get("command_class")
                        if cmd_class == "ChangeLanguageCommand":
                            action.triggered.connect(lambda checked: self._change_language_dialog())
                        elif cmd_class == "ExitCommand":
                            action.triggered.connect(lambda checked: self.close())
                        elif cmd_class == "ResetSystemCommand":
                            action.triggered.connect(lambda checked: self._execute_system_reset_direct())
                        elif cmd_class:
                            action.triggered.connect(lambda checked, c=cmd_class: self._dispatch_custom_user_command(c))
                    elif item["type"] == "submenu":
                        sub_item = item.copy()
                        sub_item["i18n_key"] = item.get("id")
                        sub_schema = { item.get("id", "sub"): sub_item }
                        self._build_menu_recursive(current_menu, sub_schema)

    def _build_tabs(self, tabs_schema: list):
        """Erstellt alle Registerkarten dynamisch und hängt den Plus-Button an."""
        import infrastructure.cfg as cfg
        
        # 1. SIGNAL-SCHUTZ AKTIVIEREN: Verhindert Fehlauslösungen beim Neuzeichnen!
        self._tabs.blockSignals(True)
    
        # Zuerst die bestehende Tableiste komplett leeren
        self._tabs.clear()
        self._tab_mapping.clear()
    
        # A) Das feste, geschützte Willkommens-Register als Basis einsetzen
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(25, 25, 25, 25)
        welcome_layout.setSpacing(12)
    
        self._lbl_welcome_head = QLabel()
        self._lbl_welcome_head.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 5px;")
        self._i18n.register(self._lbl_welcome_head, "headline", "dialog.welcome.headline")
        welcome_layout.addWidget(self._lbl_welcome_head)
    
        # KORREKTUR: Nutzt QTextBrowser für native, fehlerfreie Hyperlink-Interaktionen!
        info_area = QTextBrowser()
        info_area.setReadOnly(True)
        info_area.setStyleSheet("""
            QTextBrowser { 
                border: 1px solid #ced4da; 
                border-radius: 6px; 
                background-color: #ffffff; 
                padding: 15px; 
                font-size: 13px; 
                color: #333333;
                line-height: 1.6;
            }
        """)
        
                
        # Registriert den Info-Text mit einem festen Schlüssel im Übersetzungsservice.
        self._i18n.register(info_area, "welcome_html", "tabs.welcome.info_text")
        
        
        welcome_layout.addWidget(info_area)
        self._tabs.addTab(welcome_widget, "")
        self._tab_mapping.append((welcome_widget, "tabs.welcome.title"))
        
        # 2. Alle dynamischen Registerkarten laut unserem UI_SCHEMA aufbauen
        for tab_config in tabs_schema:
            if tab_config["id"] == "tab.welcome":
                continue
    
            tab_widget = DynamicTab(tab_config, self._services)
            tab_widget.tab_id = tab_config["id"] # Verankert die ID für das Löschen/Verschieben
            
            # Fügt das Register direkt mit dem aufgelösten Übersetzungstext hinzu!
            localized_label = self._i18n.text(tab_config["i18n_key"])
            self._tabs.addTab(tab_widget, localized_label)
            
            # Für spätere Live-Sprachwechsel im Mapping sichern
            self._tab_mapping.append((tab_widget, tab_config["i18n_key"]))
    
        # 3. Das Excel-Style "+" Tab als Auslöser ans Ende hängen (falls Limit von 10 nicht erreicht)
        if len(tabs_schema) < cfg.APP_CONFIG.get("max_tabs", 10):
            plus_dummy = QWidget() 
            self._tabs.addTab(plus_dummy, " + ")
            
            plus_tooltip = self._i18n.text("sidebar.tab.add") or "Neues Register hinzufügen"
            self._tabs.setTabToolTip(self._tabs.count() - 1, plus_tooltip)
    
        # Signalwacht wieder freischalten
        self._tabs.blockSignals(False)
    
        # Erzwingt das sofortige Übersetzen der neuen Reiter
        self.refresh_ui_texts()

  
    def _change_language_trigger(self, lang_code: str):
        """Triggert den globalen Sprachwechsel und steuert die Rechts-nach-Links-Spiegelung (RTL)."""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        import infrastructure.cfg as cfg
        import os
        import json

        # 1. JUST-IN-TIME-LADEN: Hole die Übersetzungen von der Festplatte in den RAM
        if lang_code not in self._i18n._translations:
            datei_pfad = os.path.join(cfg.JSON_LOCALES_DIR, f"{lang_code}.json")
            if os.path.exists(datei_pfad):
                try:
                    with open(datei_pfad, "r", encoding="utf-8") as f:
                        daten = json.load(f)
                        # Wir speichern es im Standard-Archiv des i18n-Dienstes
                        self._i18n._translations[lang_code] = daten.get("translations", daten)
                except Exception as e:
                    print(f"❌ [I18N] Fehler beim JIT-Laden der JSON für {lang_code}: {e}")

        # 2. BRÜCKENSCHLAG FÜR DAS INTERFACE (Once-Only / DRY):
        # Wir kopieren die dynamischen Übersetzungen direkt in das aktive Such-Wörterbuch (cfg.I18N),
        # damit self._i18n.text() die französischen Begriffe sofort findet!
        if lang_code in self._i18n._translations:
            dyn_pool = self._i18n._translations[lang_code]
            for ui_key, uebersetzter_text in dyn_pool.items():
                # Falls der Schlüssel im globalen Wörterbuch existiert, hängen wir die Sprache an
                if ui_key in cfg.I18N:
                    cfg.I18N[ui_key][lang_code] = uebersetzter_text
                else:
                    # Falls der Schlüssel neu ist (z.B. durch KI generiert), legen wir ihn an
                    cfg.I18N[ui_key] = {lang_code: uebersetzter_text}

        # 3. Sprache im zentralen I18N-Dienst umschalten
        self._i18n.change_language(lang_code)
        
        # 4. ISO-Kürzel dynamisch aus der cfg prüfen (Once-Only-Prinzip!)
        rtl_liste = getattr(cfg, "RTL_LANGUAGES", ["ar", "he", "fa"])
        if lang_code in rtl_liste:
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            
        # 5. Die Benutzeroberfläche zwingen, alle Texte synchron neu zu laden
        self.refresh_ui_texts()

    def _generate_clover_icon(self):
        """Generiert ein gestochen scharfes, blaues Kleeblatt-Vektoricon direkt im RAM."""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
        from PyQt6.QtCore import Qt, QRect
 
        # Wir erzeugen eine hochauflösende 256x256 Leinwand für Windows
        pixmap = QPixmap(256, 256)
        pixmap.fill(Qt.GlobalColor.transparent)
 
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
 
        # Professionelles Tech-Blau einstellen (Ähnlich wie das VS-Blau)
        painter.setPen(Qt.GlobalColor.transparent)
 
        # KORREKTUR: Das vierblättrige Kleeblatt (Clover) wird unzerbrechlich als Vektor geladen
        font = QFont("Segoe UI Emoji", 180)
        font.setBold(True)
        painter.setFont(font)
 
        # Das vierblättrige Kleeblatt-Symbol präzise im Zentrum platzieren
        rect = QRect(0, 0, 256, 256)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "🍀")
        painter.end()
 
        return QIcon(pixmap)

    def refresh_ui_texts(self):
        """Verankert das konfigurierte Markenzeichen im Titelbalken und übersetzt alle Tabs im Flug."""
        # 1. ICON-RETTUNG: Holt das echte Kleeblatt aus der RAM-Zeichnung und setzt das Windows-Rechteck schachmatt!
        self.setWindowIcon(self._generate_clover_icon())
        
        # 2. TITEL-BEREINIGUNG: Setzt den reinen Titelbalken absolut sauber wie bei Visual Studio!
        base_title = self._i18n.text("app.title") or "ClioGraph"
        self.setWindowTitle(base_title)
 
        # 3. TEXT-WÄCHTER: Zwingt die Willkommens-Überschrift, sich im RAM live aufzulösen
        if hasattr(self, "_lbl_welcome_head") and self._lbl_welcome_head:
            self._lbl_welcome_head.setText(self._i18n.text("dialog.welcome.headline") or "Exemplarische Vorgehensweisen")
 
        # 4. TAB-WÄCHTER: Übersetzt alle im Mapping registrierten Reiter (Willkommen / Welcome) im Flug neu
        for index, (tab_widget, i18n_key) in enumerate(self._tab_mapping):
            self._tabs.setTabText(index, self._i18n.text(i18n_key))
 
        self._i18n.translate_all()
 
        # === SIDEBAR LIVE-AKTUALISIERUNG BEI SPRACHWECHSEL ===
        # Löscht den Inhalt und das LAYOUT des IDE-Containers vollständig, um Qt-Kollisionen zu verhindern
        if hasattr(self, "_ide_container") and self._ide_container:
            from .ide_designer import IDEDesigner
            
            # Holt das aktuelle Layout des Containers
            old_layout = self._ide_container.layout()
            if old_layout:
                # 1. Alle untergeordneten Widgets und Elemente radikal zerstören
                while old_layout.count():
                    child = old_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
                # 2. Das leere Layout-Objekt selbst vom Widget entkoppeln und zerstören
                # Setzt das interne Layout-Schild auf Null zurück, damit setLayout() wieder erlaubt ist!
                from PyQt6.sip import delete as sip_delete
                sip_delete(old_layout)
            
            # 3. Über die statische Methode frisch, sauber und fehlerfrei neu injizieren
            IDEDesigner.inject_ide_sidebar_at(self, self._ide_container)
            
        # 4. Tooltip der Sidebar-Schaltfläche (Knopf 2) live aktualisieren
        if hasattr(self, "sidebar_manager") and "developer_tools" in self.sidebar_manager.sidebar_mapping:
            sidebar_entry = self.sidebar_manager.sidebar_mapping["developer_tools"]
            if isinstance(sidebar_entry, tuple):
                for item in sidebar_entry:
                    if hasattr(item, "setToolTip"):
                        dev_tooltip = self._i18n.text("sidebar.btn.developer_tool") or "Entwicklertools (VBA & GenAI)"
                        item.setToolTip(dev_tooltip)
            elif isinstance(sidebar_entry, dict) and "button" in sidebar_entry:
                dev_tooltip = self._i18n.text("sidebar.btn.developer_tool") or "Entwicklertools (VBA & GenAI)"
                sidebar_entry["button"].setToolTip(dev_tooltip)
 
        # Der asynchrone 10ms-Puffer für die Menüleisten-Neuzeichnung
        QTimer.singleShot(10, self._safe_rebuild_menu)

    def _safe_rebuild_menu(self):
        """Baut die Menüleiste sicher ausserhalb des Klick-Events und strikt nach Sortierreihenfolge neu auf."""
        import infrastructure.cfg as cfg
        self.menuBar().clear()
        
        # 1. Holen der gespeicherten Reihenfolge und der rohen Datenstruktur
        order = cfg.UI_SCHEMA.get("menu_order", [])
        structure = cfg.UI_SCHEMA.get("menu_structure", {})
        
        # Falls die Order-Liste leer sein sollte, als Schutz mit den Keys initialisieren
        if not order:
            order = list(structure.keys())
            cfg.UI_SCHEMA["menu_order"] = order
            
        # 2. Sortierte Struktur für den rekursiven Neuaufbau vorbereiten
        ordered_structure = {}
        for key in order:
            if key in structure:
                ordered_structure[key] = structure[key]
                
        # Neue Menüs absichern, die evtl. noch nicht in 'order' gelandet sind (Synchronisations-Schutz)
        for key, value in structure.items():
            if key not in ordered_structure:
                ordered_structure[key] = value
                cfg.UI_SCHEMA["menu_order"].append(key)
        
        # 3. Menü basierend auf der korrekt sortierten Struktur aufbauen
        self._build_menu_recursive(self.menuBar(), ordered_structure)
        
        # 4. Das Excel-Style Plus-Schaltfeld wieder an das sortierte Ende hängen
        current_menu_count = len(cfg.UI_SCHEMA.get("menu_structure", {}).keys())
        if current_menu_count < cfg.APP_CONFIG.get("max_main_menus", 10):
            plus_action = self.menuBar().addAction("+")
            plus_action.setToolTip(self._i18n.text("sidebar.menu.add"))
            plus_action.triggered.connect(self.create_new_main_menu)

    def _execute_macro_by_name(self, class_name):
        """Führt ein zugewiesenes Macro direkt über den Finder aus."""
        discover_func = self._services.get("command_finder")
        if discover_func:
            available = discover_func(filter_prefix=None)
            for _, instance in available.items():
                if instance.__class__.__name__ == class_name:
                    instance.execute(self._services)
                    break
  
    def _change_language_dialog(self):
        """Öffnet den Dialog zum Wechseln der Sprache basierend auf dem permanenten JSON-Zustand."""
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        import infrastructure.cfg as cfg
        import os
        import json

        # 1. DATEI-SYNCHRONISATION: Lies die freigeschalteten Sprachen direkt aus der JSON
        if os.path.exists(cfg.JSON_MENU_FILE):
            try:
                with open(cfg.JSON_MENU_FILE, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                    
                # Synchronisiere die unterstützten Sprachen aus der JSON zurück in den aktiven RAM-Pool
                if "supported_languages" in saved_data:
                    for code in saved_data["supported_languages"]:
                        if code not in cfg.APP_CONFIG["supported_languages"]:
                            cfg.APP_CONFIG["supported_languages"].append(code)
                            
                # Synchronisiere die Anzeigeliste für das GUI-Dropdown
                if "available_languages" in saved_data:
                    for lang in saved_data["available_languages"]:
                        if not any(l["code"] == lang["code"] for l in cfg.AVAILABLE_LANGUAGES):
                            cfg.AVAILABLE_LANGUAGES.append(lang)
            except Exception as e:
                print(f"[SYSTEM] Fehler beim Synchronisieren der Menü-JSON: {e}")

        # 2. GENERIERE DIE STRINGS FÜR DAS DROPDOWN (NUR AKTIVE SPRACHEN!)
        ui_dropdown_eintraege = []
        for lang in cfg.AVAILABLE_LANGUAGES:
            if lang["code"] in cfg.APP_CONFIG["supported_languages"]:
                eintrag = f"{lang['name']} [{lang['code']}]"
                if eintrag not in ui_dropdown_eintraege:
                    ui_dropdown_eintraege.append(eintrag)

        # 3. Finde den aktuellen Eintrag heraus
        current_entry = "Deutsch [de]"
        for lang in cfg.AVAILABLE_LANGUAGES:
            if lang["code"] == self._i18n._current_lang:
                current_entry = f"{lang['name']} [{lang['code']}]"
                break

        default_index = 0
        if current_entry in ui_dropdown_eintraege:
            default_index = ui_dropdown_eintraege.index(current_entry)

        # 4. Sichere Text-Fallbacks für die GUI-IDs
        title_text = self._i18n.text("dialog.language.select.title")
        if not title_text or title_text == "dialog.language.select.title":
            title_text = "Sprache wechseln / Change Language"

        prompt_text = self._i18n.text("dialog.language.select.text")
        if not prompt_text or prompt_text == "dialog.language.select.text":
            prompt_text = "Wähle eine Sprache aus / Select a language:"

        # 5. Öffnet das standardisierte Qt-Auswahlfenster
        chosen_entry, ok = QInputDialog.getItem(
            self, title_text, prompt_text, ui_dropdown_eintraege, default_index, False
        )

        # 6. Extraktion über die ISO-ID und Übergabe an den Trigger
        if ok and chosen_entry:
            chosen_code = chosen_entry.split("[")[-1].replace("]", "").strip()
            self._change_language_trigger(chosen_code)
   
    def create_new_main_menu(self):
        """Zentrale Funktion zum Erstellen eines Hauptmenüs mit permanenter UUID-ID."""
        # ONCE-ONLY & DIREKT: Wir berechnen die Zählung direkt in der Bedingung.
        # Das macht die Zuweisung absolut immun gegen NameError-Verschiebungen!
        if len(cfg.UI_SCHEMA["menu_structure"].keys()) >= cfg.APP_CONFIG.get("max_main_menus", 8):
            title = self._i18n.text("msg.protection.title") or "Limit erreicht"
            raw_msg = self._i18n.text("dialog.menu.limit_reached") or "Die maximale Anzahl von {0} Hauptmenüs wurde erreicht!"
            
            QMessageBox.warning(self, title, raw_msg.format(cfg.APP_CONFIG.get("max_main_menus", 8)))
            return

        aktuelle_sprache = self._i18n._current_lang
        bilingual_title = self._i18n.text("dialog.menu.bilingual.title") or "Bilingualer Designer"
        dialog_title = self._i18n.text("sidebar.menu.add") or "+ Neues Hauptmenü"
        
        # ONCE-ONLY: Dynamische Prompts aus den bereinigten Sprachdateien einlesen
        prompt_de = self._i18n.text("dialog.menu.prompt.de") or "Deutscher Name des Hauptmenüs:"
        prompt_en = self._i18n.text("dialog.menu.prompt.en") or "Englischer Name des Hauptmenüs:"
        
        # Dynamische Abfrage-Aufforderungen für die jeweiligen Sprachgegenstücke
        prompt_counterpart_en = "English name for '{0}':" if aktuelle_sprache == "de" else "Englischer Name für '{0}':"
        prompt_counterpart_de = "Deutscher Name für '{0}':" if aktuelle_sprache == "de" else "German counterpart for '{0}':"

        # FALL 1: Die Anwendung läuft aktuell auf DEUTSCH
        if aktuelle_sprache == "de":
            de_name, ok1 = QInputDialog.getText(self, dialog_title, prompt_de)
            if not ok1 or not de_name.strip(): return

            suggested_en = de_name.strip()
            en_name, ok2 = QInputDialog.getText(
                self, bilingual_title, prompt_counterpart_en.format(de_name.strip()), text=suggested_en
            )
            if not ok2 or not en_name.strip(): return

        # FALL 2: Dreher für andere Interface-Sprachen (z.B. Englisch) - Nutzt jetzt en.json!
        else:
            # 1. Fragt zuerst den englischen Namen mit deinem korrekten Sprach-Prompt ab
            en_name, ok1 = QInputDialog.getText(self, dialog_title, prompt_en)
            if not ok1 or not en_name.strip(): return

            suggested_de = en_name.strip()
            # 2. Fragt danach das deutsche Gegenstück ab
            de_name, ok2 = QInputDialog.getText(
                self, bilingual_title, prompt_counterpart_de.format(en_name.strip()), text=suggested_de
            )
            if not ok2 or not de_name.strip(): return

        # === UUID-ANSATZ IMPLEMENTIERUNG ===
        # Wir generieren eine unzerbrechliche ID. Ein Umbenennen ändert ab jetzt nie wieder den Schlüssel!
        menu_uuid = f"menu_{uuid.uuid4().hex[:12]}"
        unique_i18n_key = f"menu.dynamic.{menu_uuid}"

        # =====================================================================
        # SICHERHEITSANKER: VOR dem Erstellen ein "Foto" für Undo/Redo schiessen
        # =====================================================================
        if "ui_state_manager" in self._services:
            self._services["ui_state_manager"].save_checkpoint()

        # 1. Übersetzungen dauerhaft im System und physisch in JSON eintragen
        self._i18n.update_or_append_key(key=unique_i18n_key, de_text=de_name.strip(), en_text=en_name.strip())

        # 2. In die Datenstruktur (RAM) schreiben - Die UUID wird zum sicheren Anker-Key
        cfg.UI_SCHEMA["menu_structure"][menu_uuid] = {
            "i18n_key": unique_i18n_key,
            "items": []
        }
        
        # 3. In die Sortierliste für Links/Rechts-Verschiebungen eintragen
        if "menu_order" not in cfg.UI_SCHEMA:
            # Falls die Liste leer sein sollte, stellen wir sicher, dass "file" und die neue UUID drin sind
            cfg.UI_SCHEMA["menu_order"] = list(cfg.UI_SCHEMA["menu_structure"].keys())
        else:
            if menu_uuid not in cfg.UI_SCHEMA["menu_order"]:
                cfg.UI_SCHEMA["menu_order"].append(menu_uuid)

        # 4. Interface neu aufbauen
        self.setup_ui()

        # 5. Auf Festplatte sichern
        persistence = self._services.get("menu_persistence")
        if persistence and hasattr(persistence, "save_menus"):
            persistence.save_menus(cfg.UI_SCHEMA)
            
        # 6. WICHTIG: Nach dem persistenten Speichern den aktuellen Zustand im State-Manager 
        # als neuen Referenzpunkt verankern, damit 'Redo' (Wiederholen) nicht blockiert wird!
        if "ui_state_manager" in self._services:
            import copy
            # Aktualisiert das interne Backup-Foto mit den frisch geschriebenen JSON-Werten
            self._services["ui_state_manager"]._undo_stack[-1]["ui_schema"] = copy.deepcopy(cfg.UI_SCHEMA)
            if hasattr(self._i18n, "_translations"):
                self._services["ui_state_manager"]._undo_stack[-1]["translations"] = copy.deepcopy(self._i18n._translations)

        # Das neu erstellte Menü sofort als das aktive Menü für die Sidebar-Pfeile merken
        self._active_menu_uuid = menu_uuid
   
        self.statusBar().showMessage(f"Hauptmenü '{de_name.strip()}' erfolgreich über UUID-ID verankert.", 3000)

    def _dispatch_custom_user_command(self, command_string):
        """
        Die Injektor-Brücke: Importiert und führt Benutzer-Makros aus dem 
        geschützten Ordner commands_user vollautomatisch zur Laufzeit aus.
        """
        import importlib
        from PyQt6.QtWidgets import QMessageBox
        
        if not command_string:
            return
            
        # Fall 1: Klassischer eService-Adapter
        if command_string == "ExternalServiceAdapter":
            self.statusBar().showMessage("Öffne externen eService...", 3000)
            # Hier kann später dein Browser- oder API-Aufruf verankert werden
            return
            
        # Fall 2: Das konfigurierte Forscher-Makro abfangen (z.B. "business.commands_user.cmd_..." )
        user_package_prefix = "business."
        if hasattr(cfg, "USER_COMMANDS_PACKAGE"):
            user_package_prefix = cfg.USER_COMMANDS_PACKAGE
            
        if command_string.startswith(user_package_prefix):
            try:
                # Wir zerlegen den Pfad: Letztes Element = Klasse, davor = Modulpfad
                parts = command_string.split(".")
                class_name = parts[-1]
                module_path = ".".join(parts[:-1])
                
                # 1. Modul Just-in-Time aus dem RAM/Festplatte laden
                module = importlib.import_module(module_path)
                
                # 2. Die Klasse aus dem importierten Modul extrahieren
                command_class = getattr(module, class_name)
                
                # 3. Instanziieren mit Übergabe des Hauptfensters (Dependency Injection)
                command_instance = command_class(self)
                
                # 4. Befehl unzerbrechlich abfeuern
                self.statusBar().showMessage(f"Führe Anwender-Makro '{class_name}' aus...", 2000)
                command_instance.execute()
                
            except Exception as e:
                import traceback
                print(f"❌ Kritischer Fehler bei Makro-Ausführung ({command_string}): {e}")
                traceback.print_exc()
                
                # Dem Forscher ein sauberes, bilinguales Feedback bei Abstürzen geben
                lang = getattr(self._i18n, "_current_lang", "de")
                err_title = "Fehler im Benutzer-Makro" if lang == "de" else "Error in User Macro"
                err_msg = f"Das zugewiesene Makro konnte nicht ausgeführt werden.\n\nFehlerdetails:\n{str(e)}"
                QMessageBox.critical(self, err_title, err_msg)
        else:
            # Fall 3: Optimierte Systemlogik für Kern-Befehle (Ollama, Editor & Assistent)
            discover_func = self._services.get("command_finder")
            if discover_func:
                commands_dict = discover_func(filter_prefix=None)
                
                # Wir durchsuchen alle gefundenen Befehle nach dem passenden Klassennamen
                target_class = None
                for _, cmd_class in commands_dict.items():
                    # Falls es ein fertiges Objekt ist, holen wir uns dessen Klasse via type()
                    actual_class = cmd_class if isinstance(cmd_class, type) else type(cmd_class)
                    
                    if actual_class.__name__ == command_string:
                        target_class = actual_class
                        break
                
                if target_class:
                    # Instanziierung völlig parameterlos (sicher für den neuen Konstruktor!)
                    cmd_instance = target_class()
                    # Wir übergeben die zentralen System-Dienste beim Ausführen
                    cmd_instance.execute(self._services)
                else:
                    print(f"⚠️ [GUI-WARNUNG] Befehlsklasse '{command_string}' wurde im System-Pool nicht gefunden.")

    def _execute_system_reset_direct(self):
        """Sucht das Reset-Kommando im Mapping und führt es mit den korrekten Services aus."""
        from business.commands import COMMAND_MAPPING
        reset_class = COMMAND_MAPPING.get("ResetSystemCommand")
        if reset_class:
            # Dependency Injection: Wir geben die Systemdienste mit!
            cmd_instance = reset_class()
            cmd_instance.execute(self._services)
