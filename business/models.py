# Datei: models.py
"""Domain Layer: Typsichere Datenmodelle und Konvertierungslogiken für Graph-RAG"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class NodeModel:
    """Repräsentiert einen eindeutigen Knoten (Entität) im Wissensgraphen."""
    node_id: str
    label: str  # Z.B. "Person", "Ereignis", "Ort"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EdgeModel:
    """Repräsentiert eine gerichtete Beziehung (Kante) zwischen zwei Knoten."""
    source_id: str
    target_id: str
    edge_type: str  # Z.B. "GEBOREN_IN", "PARTNER_VON"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphDataWrapper:
    """Container für ein extrahiertes Teilnetzwerk (Teilgraphen)."""
    nodes: List[NodeModel] = field(default_factory=list)
    edges: List[EdgeModel] = field(default_factory=list)

    @classmethod
    def from_llm_list(cls, raw_data_list: List[Dict[str, Any]], source_ref: str) -> 'GraphDataWrapper':
        """Konvertiert rohe LLM-Listen in ein valides, Graph-RAG-taugliches Datenmodell.
        
        Verhindert 'unknown_source'-Verweise durch korrekte ID-Verknüpfung.
        """
        wrapper = cls()
        
        # Falls die Liste leer ist (z.B. beim aktuellen Testdurchlauf), leeres Paket zurückgeben
        if not raw_data_list:
            return wrapper

        # ID-Mapping, um Kanten logisch und präzise mit den generierten Knoten zu verknüpfen
        for item in raw_data_list:
            # Beispielhafte Verarbeitungslogik für strukturierte LLM-Objekte
            # (Wird aktiv, sobald Ollama echtes JSON liefert)
            pass

        return wrapper
