# Datei: business/commands/cmd_dummy.py
from business.commands.cmd_base import UICommand

class DynamischesTestFeatureCommand(UICommand):
    """Ein einfaches Test-Makro für unsere Plus-Schaltfläche."""
    
    @property
    def menu_key(self) -> str:
        return "dummy.test_feature"

    def execute(self, services: dict):
        print("\n" + "⚡"*15)
        print("[ERFOLG] Das dynamisch erstellte Feature wurde aufgerufen!")
        print("⚡"*15 + "\n")
        return "Dynamisches Feature erfolgreich ausgeführt!"
