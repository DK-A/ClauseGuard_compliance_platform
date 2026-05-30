import logging
from backend.retrieval.two_tower import TwoTowerRetrieval
from backend.reasoning.chain import ContradictionReasonerChain

logger = logging.getLogger("ClauseGuardGraphImpact")

class ResolutionImpactAnalyzer:
    def __init__(self, db_session, graph_builder):
        self.db = db_session
        self.graph_builder = graph_builder
        self.two_tower = TwoTowerRetrieval()
        self.reasoner = ContradictionReasonerChain()

    def analyze_resolution_impact(self, clause_node_id: int, proposed_edit_text: str) -> list:
        """
        Simulates the effect of modifying a clause node on all contradictions in the active graph.
        Re-evaluates semantic conflict pipelines on the edited clause against its connected neighbors.
        Returns a list of edge modifications: creation, removal, or parameter changes.
        """
        logger.info(f"Analyzing resolution simulation impact for node {clause_node_id}...")
        
        # 1. Fetch current node data from NetworkX graph
        if clause_node_id not in self.graph_builder.graph:
            logger.warning(f"Node {clause_node_id} not found in contradiction graph. No impact calculated.")
            return []
            
        target_attrs = self.graph_builder.graph.nodes[clause_node_id]
        
        # Create simulated version of this clause with modified text
        simulated_clause = {
            "text": proposed_edit_text,
            "clause_type": target_attrs.get("clause_type"),
            "section_heading": target_attrs.get("section"),
            "page_number": target_attrs.get("page_number"),
            "source_document": target_attrs.get("doc_source"),
            "vector_id": f"sim-{clause_node_id}"
        }
        
        impacts = []
        
        # 2. Find all current neighbors (connected conflicts) in the graph
        neighbors = list(self.graph_builder.graph.successors(clause_node_id)) + \
                    list(self.graph_builder.graph.predecessors(clause_node_id))
        neighbors = list(set(neighbors))  # Deduplicate
        
        for neighbor_id in neighbors:
            neighbor_attrs = self.graph_builder.graph.nodes[neighbor_id]
            
            # Form simulated pair
            n_clause = {
                "text": neighbor_attrs.get("text"),
                "clause_type": neighbor_attrs.get("clause_type"),
                "section_heading": neighbor_attrs.get("section"),
                "page_number": neighbor_attrs.get("page_number"),
                "source_document": neighbor_attrs.get("doc_source"),
                "vector_id": f"neighbor-{neighbor_id}"
            }
            
            # Re-run reasoning between the proposed edit and the neighbor
            analysis = self.reasoner.analyze_pair(proposed_edit_text, n_clause["text"])
            relationship = analysis.get("relationship", "NO_CONFLICT")
            
            # Fetch existing edge attributes to compare changes
            existing_edge = None
            direction = "forward"
            if self.graph_builder.graph.has_edge(clause_node_id, neighbor_id):
                existing_edge = self.graph_builder.graph[clause_node_id][neighbor_id]
                direction = "forward"
            elif self.graph_builder.graph.has_edge(neighbor_id, clause_node_id):
                existing_edge = self.graph_builder.graph[neighbor_id][clause_node_id]
                direction = "reverse"
                
            if relationship == "NO_CONFLICT":
                # Current conflict will be successfully RESOLVED by the edit
                impacts.append({
                    "type": "REMOVED",
                    "neighbor_id": neighbor_id,
                    "neighbor_text": n_clause["text"],
                    "document": n_clause["source_document"],
                    "description": f"Conflict resolved with {n_clause['source_document']} section {n_clause['section_heading']}"
                })
            else:
                # The conflict persists but its properties may have changed
                severity_changed = False
                if existing_edge and existing_edge.get("severity") != analysis.get("severity"):
                    severity_changed = True
                    
                impacts.append({
                    "type": "CHANGED" if severity_changed else "PERSISTS",
                    "neighbor_id": neighbor_id,
                    "neighbor_text": n_clause["text"],
                    "document": n_clause["source_document"],
                    "old_severity": existing_edge.get("severity") if existing_edge else "UNKNOWN",
                    "new_severity": analysis.get("severity"),
                    "description": f"Conflict severity shifts from {existing_edge.get('severity') if existing_edge else 'HIGH'} to {analysis.get('severity')} with {n_clause['source_document']}"
                })
                
        return impacts
