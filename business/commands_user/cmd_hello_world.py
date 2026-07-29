# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QMessageBox

class HelloWorldCommand:
    """Ein einfaches Test-Makro zur Validierung der Befehls-Zuweisung."""
    
    def __init__(self, main_window):
        self.win = main_window

    def execute(self):
        """Wird aufgerufen, wenn der Forscher auf den zugewiesenen Menüpunkt klickt."""
        # Ermittle die aktuelle GUI-Sprache für den bilingualen Test
        lang = getattr(self.win._i18n, "_current_lang", "de")
        
        title = "ClioGraph Test" if lang == "de" else "ClioGraph Test"
        msg = "Hallo Welt! Die Befehls-Zuordnung funktioniert einwandfrei!" if lang == "de" else "Hello World! The command assignment works perfectly!"
        
        QMessageBox.information(self.win, title, msg)
