# Datei: exceptions.py
"""Domain Layer: Spezifische Ausnahme-Klassen für das ClioGraph-System"""

class ClioGraphError(Exception):
    """Basis-Ausnahme für das gesamte ClioGraph-System. 
    Alle spezifischen Fehler erben von dieser Klasse.
    """
    pass

class DatabaseConnectionError(ClioGraphError):
    """Wird geworfen, wenn die Kùzu-Datenbank nicht erreichbar ist 
    oder eine Graph-Abfrage fehlschlägt.
    """
    pass

class LlmTimeoutError(ClioGraphError):
    """Wird geworfen, wenn das lokale Ollama-Modell (z.B. llama3:science) 
    nicht antwortet oder die API blockiert ist.
    """
    pass

class GraphValidationError(ClioGraphError):
    """Wird geworfen, wenn die vom LLM gelieferten JSON-Daten unvollständig 
    sind oder Beziehungen (Kanten) ohne gültige Knoten erzeugt wurden.
    """
    pass
