# Datei: infrastructure/llm_ml/llm.py
"""Infrastructure Layer: Kapselung des lokalen LLM-Dienstes via Ollama"""
from infrastructure.exceptions import LlmTimeoutError
import infrastructure.cfg as cfg

class LlmExtractionService:
    """Verwaltet die Abfragen an das lokale Ollama-Modell zur Entitätenextraktion."""
    
    def __init__(self, model_name: str = cfg.APP_CONFIG["default_model"]):
        # Falls kein Modell übergeben wird, nimm automatisch den Standard aus der cfg
        self._model_name = model_name
    
    def extract_entities_and_relations(self, text: str) -> list:
        """Sendet Rohtext an Ollama und erwartet eine strukturierte Liste zurück.
        
        Fängt Verbindungs- und Timeout-Fehler ab und reicht sie als Business-Error weiter.
        """
        try:
            # Platzhalter für den echten Ollama API-Aufruf
            # Später: response = ollama.chat(model=self._model_name, ...)
            print(f"[Infrastructure] Sende Text an Ollama-Modell '{self._model_name}'...")
            
            # Temporäre Test-Rückgabe (wird bald durch echte LLM-Logik ersetzt)
            return []
        except Exception as e:
            # Technische API-Abstürze in saubere Business-Exception verpacken
            raise LlmTimeoutError(f"Ollama-Modell '{self._model_name}' antwortet nicht: {str(e)}")
