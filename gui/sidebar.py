"""Presentation Layer: Modulares VS-Code-Style Sidebar-Framework.
Verwaltet eine schmale Icon-Leiste (ActivityBar) und ein StackedWidget für wechselnde Sidebar-Inhalte."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt

class SidebarController(QWidget):
    """Das zentrale Kontrollzentrum für alle linken Sidebars (Icon-Leiste + Inhalts-Stack)."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.active_id = None  # Speichert, welche Sidebar gerade offen ist
        
        # Horizontales Layout: [ Schmale Icon-Leiste | Großer Inhalts-Stack ]
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        # 1. Die schmale Icon-Leiste (Activity Bar)
        self.activity_bar = QWidget()
        self.activity_bar.setFixedWidth(46)
        self.activity_bar.setStyleSheet("""
            QWidget { background-color: #f1f3f5; border-right: 1px solid #ced4da; }
            QPushButton { background: transparent; border: none; font-size: 14px; padding: 10px 0px; }
            QPushButton:hover { background-color: #e9ecef; }
            QPushButton:checked { background-color: #ffffff; border-left: 3px solid #007acc; }
        """)
        self.activity_layout = QVBoxLayout()
        self.activity_layout.setContentsMargins(0, 5, 0, 0)
        self.activity_layout.setSpacing(5)
        self.activity_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.activity_bar.setLayout(self.activity_layout)
        self.layout.addWidget(self.activity_bar)
        
        # 2. Der Inhalts-Stack für die eigentlichen Sidebars
        self.content_stack = QStackedWidget()
        self.content_stack.setFixedWidth(220)  # Feste Breite für das ausgeklappte Menü
        self.layout.addWidget(self.content_stack)
        
        self.sidebar_mapping = {}  # ID -> (Widget, Button)

    def register_sidebar(self, sidebar_id: str, icon_text: str, widget: QWidget, tooltip: str = ""):
        """Registriert ein neues Sidebar-Panel im System."""
        btn = QPushButton(icon_text)
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setFixedSize(46, 32)
        btn.clicked.connect(lambda: self.toggle_sidebar(sidebar_id))
        
        self.activity_layout.addWidget(btn)
        self.content_stack.addWidget(widget)
        self.sidebar_mapping[sidebar_id] = (widget, btn)

    def toggle_sidebar(self, sidebar_id: str):
        """Wechselt die Sidebar oder schließt sie komplett, wenn sie bereits aktiv war."""
        target_widget, target_btn = self.sidebar_mapping[sidebar_id]
        
        # Fall 1: Bereits offen -> Schließen
        if self.active_id == sidebar_id:
            self.content_stack.hide()
            target_btn.setChecked(False)
            self.active_id = None
            self.main_window._main_splitter.setSizes([46, self.main_window.width() - 46])
            
        # Fall 2: Öffnen / Wechseln
        else:
            for sid, (_, btn) in self.sidebar_mapping.items():
                if sid != sidebar_id:
                    btn.setChecked(False)
            
            target_btn.setChecked(True)
            self.content_stack.setCurrentWidget(target_widget)
            self.content_stack.show()
            self.active_id = sidebar_id
            self.main_window._main_splitter.setSizes([266, self.main_window.width() - 266])
