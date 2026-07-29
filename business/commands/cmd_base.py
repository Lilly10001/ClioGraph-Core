# Datei: business/commands/cmd_base.py
from abc import ABC, abstractmethod

class UICommand(ABC):
    """
    Erweiterte abstrakte Basisklasse für alle entkoppelten Menübefehle.
    Erzwingt Typsicherheit für die dynamische Menügenerierung.
    """
    
    @property
    @abstractmethod
    def menu_key(self) -> str:
        """
        Gibt den exakten I18N-Konfigurationsschlüssel des Befehls zurück.
        Muss von jeder Kind-Klasse überschrieben werden (z.B. 'menu.file.export').
        """
        pass
        
    @abstractmethod
    def execute(self, services: dict):
        """Führt den spezifischen Business-Befehl aus."""
        pass
