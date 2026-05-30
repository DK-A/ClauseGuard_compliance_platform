import logging
from backend.config import get_reasoning_config
from backend.retrieval.vectorstore import VectorStore

logger = logging.getLogger("ClauseGuardTwoTower")

# Conflict compatibility matrix rules (Symmetric check)
COMPATIBILITY_CONFLICT_PAIRS = {
    ("obligation", "prohibition"),
    ("prohibition", "obligation"),
    ("permission", "prohibition"),
    ("prohibition", "permission"),
    ("obligation", "permission"),
    ("permission", "obligation")
}

class TwoTowerRetrieval:
    def __init__(self):
        self.vector_store = VectorStore()
        
    def find_contradiction_candidates(self, query_clause: dict, all_clauses_in_db: list) -> list:
        """
        Retrieves candidate matching pairs using Two-Tower methodology.
        - Tower 1: Semantic search top-20 closest matches from vector DB.
        - Tower 2: Compatibility filter based on logic matrix + excludes same-document pairs.
        - Caps output based on hardware profile limits.
        """
        config = get_reasoning_config()
        pair_limit = config.pair_limit
        
        query_text = query_clause["text"]
        query_doc = query_clause["metadata"]["source_document"] if "metadata" in query_clause else query_clause.get("source_document")
        query_type = query_clause.get("clause_type")
        
        # Tower 1: Semantic search
        semantic_results = self.vector_store.query_similarity(
            query_text=query_text,
            n_results=20,
            filter_document=query_doc
        )
        
        candidates = []
        
        # Match each vector query output through Tower 2 filter
        for match in semantic_results:
            match_doc = match["metadata"]["source_document"]
            match_type = match["metadata"]["clause_type"]
            
            # Exclude same document matching (extra safety guard)
            if query_doc == match_doc:
                continue
                
            # Tower 2: Category matrix check
            type_tuple = (query_type, match_type)
            if type_tuple in COMPATIBILITY_CONFLICT_PAIRS:
                candidates.append({
                    "clause_a": query_clause,
                    "clause_b": match,
                    "cosine_similarity": match["similarity"]
                })
                
        # Return candidates sorted by similarity, capped at hardware limit
        candidates.sort(key=lambda x: x["cosine_similarity"], reverse=True)
        return candidates[:pair_limit]
