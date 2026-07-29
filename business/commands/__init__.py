# Datei: business/commands/__init__.py
# Zentrale Bereitstellung aller Menübefehle für den Service Locator

from .cmd_file import ProjectExportCommand, OllamaInfoCommand, OllamaValidateCommand, LanguageEditorCommand
from .cmd_system import ResetSystemCommand 

# Mapping für die dynamische Befehlsinstanziierung zur Laufzeit
COMMAND_MAPPING = {
    "menu.file.export": ProjectExportCommand,
    "menu.file.ollama": OllamaInfoCommand,
    "menu.file.validate": OllamaValidateCommand,
    "menu.file.edit_locales": LanguageEditorCommand,
    
    # Variante 1: Registrierung über die ID
    "menu.file.reset_system": ResetSystemCommand,
    
     # Variante 2: Registrierung über den Klassennamen (ERWEITERT FÜR DEINE BEIDEN BUTTONS)
    "ResetSystemCommand": ResetSystemCommand,
    "OllamaValidateCommand": OllamaValidateCommand,   
    "LanguageEditorCommand": LanguageEditorCommand   
}