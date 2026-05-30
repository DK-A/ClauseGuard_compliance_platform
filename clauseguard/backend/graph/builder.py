import networkx as nx
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger("ClauseGuardGraphBuilder")

class ContradictionGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def clear(self):
        self.graph.clear()

    def add_clause_node(self, clause_id: int, text: str, doc_source: str, clause_type: str, page_number: int, section: str, entity_metadata: dict):
        """
        Registers a clause node in the NetworkX graph.
        """
        self.graph.add_node(
            clause_id,
            clause_id=clause_id,
            text=text,
            doc_source=doc_source,
            clause_type=clause_type,
            page_number=page_number,
            section=section,
            entity_metadata=entity_metadata
        )

    def add_contradiction_edge(self, edge_id: int, clause_a_id: int, clause_b_id: int, contradiction_type: str, severity: str, confidence: float, status: str = "open", resolution_text: str = ""):
        """
        Adds a typed edge between two conflicting clause nodes.
        """
        self.graph.add_edge(
            clause_a_id,
            clause_b_id,
            edge_id=edge_id,
            contradiction_type=contradiction_type,  # DIRECT_CONTRADICTION, PARTIAL_OVERLAP, etc.
            severity=severity,  # CRITICAL, HIGH, etc.
            confidence=confidence,
            status=status,  # open, resolved, dismissed
            resolution_text=resolution_text
        )

    def get_cluster(self, node_id: int) -> Dict[str, Any]:
        """
        Extracts all nodes and edges within a 2-hop radius around target node.
        """
        if node_id not in self.graph:
            return {"nodes": [], "edges": []}
            
        # Treat as undirected for neighborhood calculations
        undirected_g = self.graph.to_undirected()
        try:
            lengths = nx.single_source_shortest_path_length(undirected_g, node_id, cutoff=2)
            hop_nodes = list(lengths.keys())
        except Exception:
            hop_nodes = [node_id]
            
        subgraph = self.graph.subgraph(hop_nodes)
        return self._serialize_subgraph(subgraph)

    def get_chain(self, node_id: int) -> List[List[int]]:
        """
        Identifies transitive contradiction paths originating from or passing through a node.
        e.g., Clause A contradicts Clause B, which conflicts with Clause C.
        """
        if node_id not in self.graph:
            return []
            
        chains = []
        # Run a simple DFS search to find paths up to length 4
        undirected_g = self.graph.to_undirected()
        for target in undirected_g.nodes:
            if target == node_id:
                continue
            try:
                paths = list(nx.all_simple_paths(undirected_g, node_id, target, cutoff=3))
                if paths:
                    chains.extend(paths)
            except Exception:
                pass
                
        # Deduplicate paths
        unique_chains = []
        for path in chains:
            if path not in unique_chains:
                unique_chains.append(path)
                
        return unique_chains[:5]

    def _serialize_subgraph(self, sg) -> Dict[str, Any]:
        """
        Converts a NetworkX subgraph to React Flow format.
        """
        nodes = []
        edges = []
        
        # Mapping colors based on document sources
        doc_sources = list(set(nx.get_node_attributes(sg, "doc_source").values()))
        doc_color_map = {}
        colors = ["#b4c5ff", "#ffb596", "#c6c6cd", "#ffb4ab", "#8d90a0"]
        for idx, src in enumerate(doc_sources):
            doc_color_map[src] = colors[idx % len(colors)]
            
        # Vertical layout counters per document source
        doc_node_counters = {}
        for src in doc_sources:
            doc_node_counters[src] = 0

        for node_id, attrs in sg.nodes(data=True):
            src = attrs.get("doc_source", "unknown_doc")
            color = doc_color_map.get(src, "#b4c5ff")
            
            col_idx = doc_sources.index(src) if src in doc_sources else 0
            row_idx = doc_node_counters[src]
            doc_node_counters[src] += 1
            
            # Position layout: 450px horizontal column gap, 280px vertical row gap
            x_pos = 100 + col_idx * 450
            y_pos = 100 + row_idx * 280
            
            nodes.append({
                "id": str(node_id),
                "type": "customNode",
                "data": {
                    "label": f"{attrs.get('section', 'Clause')} (p.{attrs.get('page_number', 1)})",
                    "text": attrs.get("text", ""),
                    "doc_source": attrs.get("doc_source", ""),
                    "clause_type": attrs.get("clause_type", ""),
                    "color": color
                },
                "position": {"x": x_pos, "y": y_pos}
            })
            
        for u, v, attrs in sg.edges(data=True):
            c_type = attrs.get("contradiction_type", "DIRECT_CONTRADICTION")
            
            # Map edge stroke colors
            edge_color = "#ef4444"  # Default red
            if c_type == "PARTIAL_OVERLAP":
                edge_color = "#f59e0b"  # Amber
            elif c_type == "SUPERSESSION":
                edge_color = "#2563eb"  # Cobalt
            elif c_type == "AMBIGUITY":
                edge_color = "#a855f7"  # Muted purple
                
            edges.append({
                "id": f"e-{u}-{v}-{attrs.get('edge_id')}",
                "source": str(u),
                "target": str(v),
                "label": c_type,
                "animated": attrs.get("status") == "open",
                "style": {"stroke": edge_color, "strokeWidth": 2},
                "data": {
                    "severity": attrs.get("severity"),
                    "confidence": attrs.get("confidence"),
                    "status": attrs.get("status"),
                    "resolution_text": attrs.get("resolution_text")
                }
            })
            
        return {"nodes": nodes, "edges": edges}

    def serialize_for_frontend(self) -> Dict[str, Any]:
        """
        Serializes the complete DiGraph to React Flow format.
        """
        return self._serialize_subgraph(self.graph)
