# Datei: database/db.py
"""Data Access Layer (DAL): Kapselung der Kùzu-Graphdatenbank"""
from infrastructure.exceptions import DatabaseConnectionError
import infrastructure.cfg as cfg

class GraphRepository:
    """Verwaltet den Zugriff auf die lokale Kùzu-Graphdatenbank."""
    
    def __init__(self, db_path: str = cfg.DB_PATH):
        self._db_path = db_path
        # Hier wird später die echte Kùzu-Verbindung instanziiert
        self._db = None
        self._session = None
        # Open Item: Schema-Erstellung (cfg.NODE_LABELS & cfg.EDGE_TYPES) bei der 
        # Datenbank-Initialisierung dynamisch einlesen (geplant für Phase 2).

    def insert_graph_data(self, graph_data_wrapper) -> bool:
        """Speichert extrahierte Knoten und Kanten in der Datenbank.
        
        Fängt interne Kùzu-Ausnahmen ab und übersetzt sie in Business-Fehler.
        """
        try:
            # Platzhalter für die echte Kùzu-Transaktionslogik
            # Später: self._session.execute(...)
            print(f"[DAL] Speichere {len(graph_data_wrapper.nodes)} Knoten in '{self._db_path}'...")
            return True
        except Exception as e:
            # Rohe C++/Treiber-Fehler abfangen und als sauberen Fehler hochreichen
            raise DatabaseConnectionError(f"Fehler beim Schreiben in die Kùzu-Datenbank: {str(e)}")
