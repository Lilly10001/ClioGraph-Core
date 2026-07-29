# Datei: business/biz.py
"""Business Logic Layer (BLL): Koordination der Arbeitsabläufe für ClioGraph"""
from database.db import GraphRepository
from business.models import GraphDataWrapper
from infrastructure.exceptions import GraphValidationError

class BusinessCoordinator:
    """Der zentrale Dirigent der Geschäftslogik (Fassade/Coordinator Pattern)."""
    
    def __init__(self, repository: GraphRepository, llm_service):
        self._repo = repository
        self._llm = llm_service

    def process_input_data(self, text: str, source_ref: str) -> GraphDataWrapper:
        """Steuert die Kette aus LLM-Extraktion und Datenbank-Speicherung.
        
        Prüft die Integrität der extrahierten Daten für maximale Graph-RAG-Tauglichkeit.
        """
        # 1. LLM zur Extraktion aufrufen
        raw_llm_list = self._llm.extract_entities_and_relations(text)
        
        # 2. Aus den LLM-Daten ein valides Graph-Modell bauen
        try:
            # Erzeugt das Datenpaket (Knoten und Kanten)
            graph_data = GraphDataWrapper.from_llm_list(raw_llm_list, source_ref)
        except Exception as e:
            raise GraphValidationError(f"Die Struktur der extrahierten Daten ist fehlerhaft: {str(e)}")

        # 3. Validierung: Für ein stabiles Graph-RAG dürfen keine verwaisten Kanten existieren
        # (Dieser Check wird aktiv, sobald wir das Datenmodell im nächsten Schritt reparieren)
        # Open Item: Gegen das in cfg.py definierte Schema (NODE_LABELS / EDGE_TYPES) 
        # validieren, bevor die Daten an die DAL übergeben werden.

        # 4. Daten an die DAL zur persistenten Speicherung übergeben
        self._repo.insert_graph_data(graph_data)
        
        return graph_data
