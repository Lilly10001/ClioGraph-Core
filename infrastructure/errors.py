# Datei: infrastructure/errors.py
"""Infrastructure/Utility Layer: Gekapselter und unabhängiger Fehler-Service"""
import logging
import infrastructure.cfg as cfg
from infrastructure.exceptions import (
    ClioGraphError, DatabaseConnectionError, 
    LlmTimeoutError, GraphValidationError
)

# Einfaches Logging in eine Datei aktivieren
logging.basicConfig(
    filename=cfg.LOG_FILE_PATH, 
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class ErrorHandlingService:
    def __init__(self, i18n_service):
        self._i18n = i18n_service
        # Zuordnung von Ausnahmen zu ihren Übersetzungs-Schlüsseln oder Präfixen
        self._error_map = {
            ValueError: "error.validation",
            GraphValidationError: "error.graph_data",
            DatabaseConnectionError: "error.database",
            LlmTimeoutError: "error.llm",
            ClioGraphError: "error.generic"
        }

    def handle_exception(self, exception: Exception) -> str:
        """Loggt den Fehler und gibt eine saubere, lokalisierte Nachricht zurück."""
        # 1. Fehler im Hintergrund protokollieren
        logging.error(f"Ausnahme abgefangen: {str(exception)}", exc_info=True)
        
        # 2. Passenden Übersetzungs-Präfix ermitteln
        for error_cls, cfg_key in self._error_map.items():
            if isinstance(exception, error_cls):
                # Nutzen des bestehenden i18n-Service für die Übersetzung
                prefix = self._i18n.text(cfg_key)
                return cfg.ERROR_UI_FORMAT.format(prefix=prefix, message=str(exception))
        
        # Fallback für unvorhergesehene Systemfehler
        fallback_msg = self._i18n.text("error.unknown")
        return cfg.ERROR_UI_FORMAT.format(prefix=fallback_msg, message=str(exception))
