# -*- coding: utf-8 -*-
"""Presentation Layer: Dynamisches Registerkarten-Framework (Tabs) mit automatischer Layout-Segmentierung"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, QMessageBox
from PyQt6.QtCore import Qt
from .factory import WidgetFactory

class DynamicTab(QWidget):
    """Generischer Tab, der seine UI-Elemente rein aus dem Schema generiert und komplexe Segmente aufbaut."""
    

    def __init__(self, tab_config: dict, services: dict):
        super().__init__()
        self._services = services
        self._i18n = services["i18n"]
        self._element_registry = {} # Kapselung: Hält Referenzen auf die Felder für die Businesslogik
        
        # Speichere die ID des aktuellen Tabs (Wichtig für die automatische Code-Generierung!)
        self.tab_id = tab_config.get("id", "unknown_tab")
        self._layout_type = tab_config.get("layout_type", "form")

        # =====================================================================
        # BOOTSTRAPPING DER SCROLLBAR-INFRASTRUKTUR (Absolut absturzsicher)
        # =====================================================================
        from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
        
        # 1. Das äußere Haupt-Layout des Tabs bekommt eine ScrollArea injiziert
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        outer_layout.addWidget(self.scroll_area)
        
        # 2. Die eigentliche Leinwand ("Canvas"), auf der die absoluten Elemente platziert werden
        self.canvas_widget = QWidget()
        self.scroll_area.setWidget(self.canvas_widget)
        
        # 3. Unser inneres Haupt-Layout wird nun an das Canvas-Widget gekoppelt!
        # NEU: Das Layout steuert nicht mehr das canvas_widget direkt!
        self._main_layout = QVBoxLayout()
        self.canvas_widget.setLayout(self._main_layout)
        self._main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Initialisiere die Segment-Container aus der JSON-Datei
        self._build_tab_geometry(tab_config.get("elements", []))

    def _build_tab_geometry(self, elements_schema: list):
        """Erzeugt rahmenlose Segmente basierend auf dem gewählten Layout-Typen."""
        if self._layout_type == "form":
            # Klassisches Formular: Elemente werden direkt untereinander gereiht
            for elem in elements_schema:
                self._create_and_append_widget(elem, self._main_layout)
            
            # Ein Stretch ganz unten sorgt für die adäquate Ausrichtung
            self._main_layout.addStretch()

        elif self._layout_type == "split_horizontal":
            from PyQt6.QtWidgets import QSplitter
            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.setStyleSheet("QSplitter::handle { background-color: #ced4da; }")
            splitter.setHandleWidth(4)

            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            left_layout.setContentsMargins(0, 0, 0, 0)

            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.setContentsMargins(0, 0, 0, 0)

            for elem in elements_schema:
                pane = elem.get("pane", "left")
                target_layout = right_layout if pane == "right" else left_layout
                self._create_and_append_widget(elem, target_layout)

            splitter.addWidget(left_widget)
            splitter.addWidget(right_widget)
            self._main_layout.addWidget(splitter)

        elif self._layout_type == "split_vertical":
            from PyQt6.QtWidgets import QSplitter
            splitter = QSplitter(Qt.Orientation.Vertical)
            splitter.setStyleSheet("QSplitter::handle { background-color: #ced4da; }")
            splitter.setHandleWidth(4)

            top_widget = QWidget()
            top_layout = QVBoxLayout(top_widget)
            top_layout.setContentsMargins(0, 0, 0, 0)

            bottom_widget = QWidget()
            bottom_layout = QVBoxLayout(bottom_widget)
            bottom_layout.setContentsMargins(0, 0, 0, 0)

            for elem in elements_schema:
                pane = elem.get("pane", "top")
                target_layout = bottom_layout if pane == "bottom" else top_layout
                self._create_and_append_widget(elem, target_layout)

            splitter.addWidget(top_widget)
            splitter.addWidget(bottom_widget)
            self._main_layout.addWidget(splitter)


    def _create_and_append_widget(self, elem_config: dict, target_layout):
        """Hilfsfunktion zur Platzierung der Elemente auf der Leinwand."""
        # Generierung über deine Widget-Fabrik
        widget = WidgetFactory.create_widget(elem_config, self._services, self._element_registry)
        
        if widget:
            # INTERNER TRANSITIONS-SCHUTZ: Prüft, ob canvas_widget existiert
            target_canvas = getattr(self, "canvas_widget", self)
            
            if "x" in elem_config and "y" in elem_config:
                # Das Widget muss ein Kind unseres Canvas-Widgets sein!
                widget.setParent(target_canvas)
                widget.move(int(elem_config["x"]), int(elem_config["y"]))
                widget.show()
                
                # Wir erweitern die Leinwand-Größe dynamisch, damit die Scrollbalken anspringen
                if hasattr(self, "canvas_widget"):
                    needed_w = int(elem_config["x"]) + widget.width() + 40
                    needed_h = int(elem_config["y"]) + widget.height() + 40
                    self.canvas_widget.setMinimumSize(
                        max(self.canvas_widget.minimumWidth(), needed_w),
                        max(self.canvas_widget.minimumHeight(), needed_h)
                    )
            else:
                # Ansonsten wird es normal in den Layout-Sizer eingepflegt
                target_layout.addWidget(widget)

        # =====================================================================
        # LIVE-REPAINT TRIGGER: Erzwingt das physische Rendern auf Klassenebene
        # =====================================================================
        if widget:
            widget.updateGeometry()
            widget.repaint()

    
    def _execute_assigned_command(self, command_class_name: str):
        """Sucht das zuständige Command und übergibt die Daten des Tabs an die Business-Logik."""
        if not command_class_name:
            return
            
        discover_func = self._services.get("command_finder")
        if not discover_func:
            return
            
        available_macros = discover_func(filter_prefix=None)
        for _, cmd_instance in available_macros.items():
            if cmd_instance.__class__.__name__ == command_class_name:
                # Kapselung: Das Business-Command erhält NUR das i18n-entkoppelte Datenpaket
                if hasattr(cmd_instance, "execute_with_ui_context"):
                    cmd_instance.execute_with_ui_context(self._services, self._element_registry)
                else:
                    cmd_instance.execute(self._services)
                break

    def add_element_live(self, element_config: dict):
        """Fügt ein neues Excel-Steuerelement zur Laufzeit live in dieses Register ein."""
        services = self._services
        
        # Live-Generierung über deine Fabrik
        new_widget = WidgetFactory.create_widget(element_config, services, self._element_registry)
        
        if new_widget is not None:
            # SCHUTZ-FALLBACK: Falls canvas_widget (noch) nicht existiert, nutzen wir das Register selbst
            target_canvas = getattr(self, "canvas_widget", self)
            
            if "x" in element_config and "y" in element_config:
                # Absolute Platzierung zur Laufzeit
                new_widget.setParent(target_canvas)
                new_widget.move(int(element_config["x"]), int(element_config["y"]))
                
                # Scroll-Leinwand anpassen (nur wenn canvas_widget physisch existiert)
                if hasattr(self, "canvas_widget"):
                    needed_w = int(element_config["x"]) + new_widget.width() + 40
                    needed_h = int(element_config["y"]) + new_widget.height() + 40
                    self.canvas_widget.setMinimumSize(
                        max(self.canvas_widget.minimumWidth(), needed_w),
                        max(self.canvas_widget.minimumHeight(), needed_h)
                    )
            else:
                # Sizer-Fallklasse (Fallback)
                if hasattr(self, "_main_layout"):
                    count = self._main_layout.count()
                    if count > 1:
                        self._main_layout.insertWidget(count - 1, new_widget)
                    else:
                        self._main_layout.addWidget(new_widget)
            
            # Element-ID registrieren
            elem_id = element_config.get("id")
            self._element_registry[elem_id] = new_widget
            
            # Physisches Zeichnen erzwingen
            new_widget.show()
            if hasattr(self, "_main_layout"):
                self._main_layout.invalidate()
                self._main_layout.activate()
            self.updateGeometry()
            self.repaint()