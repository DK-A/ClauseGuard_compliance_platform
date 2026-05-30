import os
import logging
from backend.config import CHROMA_PATH
from backend.retrieval.embedder import Embedder

logger = logging.getLogger("ClauseGuardVectorStore")

class VectorStore:
    def __init__(self):
        self.embedder = Embedder()
        self.client = None
        self.collection = None
        self.fallback_db = {}  # In-memory backup database
        self.use_fallback = False
        
        try:
            import chromadb
            # Initialize local sqlite-based persistent client
            self.client = chromadb.PersistentClient(path=CHROMA_PATH)
            self.collection = self.client.get_or_create_collection(
                name="clauseguard_clauses",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB persistent client successfully initialized.")
        except Exception as e:
            logger.warning(f"Could not load chromadb: {e}. Falling back to clean in-memory vector store.")
            self.use_fallback = True

    def add_clauses(self, clauses: list, source_document: str):
        """
        Embeds a batch of clause dictionaries and stores them in ChromaDB/Fallback.
        """
        if not clauses:
            return
            
        texts = [c["text"] for c in clauses]
        ids = [c["vector_id"] for c in clauses]
        embeddings = self.embedder.embed_batch(texts)
        
        # Format metadata
        metadatas = []
        for c in clauses:
            metadatas.append({
                "source_document": source_document,
                "clause_type": c["clause_type"],
                "section_heading": c["section_heading"],
                "page_number": c["page_number"]
            })
            
        if self.use_fallback:
            for idx, text, vector_id, meta in zip(range(len(texts)), texts, ids, metadatas):
                self.fallback_db[vector_id] = {
                    "text": text,
                    "embedding": embeddings[idx],
                    "metadata": meta
                }
        else:
            try:
                # Convert list-based types for json compatibility
                # Standard scalar values in metadata
                self.collection.add(
                    ids=ids,
                    documents=texts,
                    embeddings=[list(map(float, emb)) for emb in embeddings],
                    metadatas=metadatas
                )
            except Exception as e:
                logger.error(f"Error adding to ChromaDB: {e}. Writing to fallback DB.")
                for idx, text, vector_id, meta in zip(range(len(texts)), texts, ids, metadatas):
                    self.fallback_db[vector_id] = {
                        "text": text,
                        "embedding": embeddings[idx],
                        "metadata": meta
                    }

    def query_similarity(self, query_text: str, n_results: int = 20, filter_document: str = None) -> list:
        """
        Queries the vector store for top-K semantically similar clauses, excluding same-document if specified.
        """
        query_vector = self.embedder.embed_text(query_text)
        
        results = []
        
        if self.use_fallback or not self.collection:
            # Manual in-memory Cosine Similarity
            import numpy as np
            q_vec = np.array(query_vector)
            
            candidates = []
            for vid, item in self.fallback_db.items():
                if filter_document and item["metadata"]["source_document"] == filter_document:
                    continue
                
                i_vec = np.array(item["embedding"])
                dot = np.dot(q_vec, i_vec)
                norm_q = np.linalg.norm(q_vec)
                norm_i = np.linalg.norm(i_vec)
                
                if norm_q > 0 and norm_i > 0:
                    sim = float(dot / (norm_q * norm_i))
                else:
                    sim = 0.0
                    
                candidates.append({
                    "vector_id": vid,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "similarity": sim
                })
                
            # Sort by highest similarity
            candidates.sort(key=lambda x: x["similarity"], reverse=True)
            results = candidates[:n_results]
        else:
            try:
                # Build metadata search dictionary
                where_dict = {}
                if filter_document:
                    where_dict = {"source_document": {"$ne": filter_document}}
                    
                chroma_results = self.collection.query(
                    query_embeddings=[list(map(float, query_vector))],
                    n_results=n_results,
                    where=where_dict if where_dict else None
                )
                
                if chroma_results and "ids" in chroma_results and chroma_results["ids"]:
                    ids = chroma_results["ids"][0]
                    documents = chroma_results["documents"][0]
                    metadatas = chroma_results["metadatas"][0]
                    # Cosine distance in Chroma: lower distance means higher similarity.
                    # Cosine similarity = 1 - Cosine Distance
                    distances = chroma_results["distances"][0] if "distances" in chroma_results else [0.0]*len(ids)
                    
                    for idx in range(len(ids)):
                        sim = float(1.0 - distances[idx])
                        results.append({
                            "vector_id": ids[idx],
                            "text": documents[idx],
                            "metadata": metadatas[idx],
                            "similarity": sim
                        })
            except Exception as e:
                logger.error(f"Error querying ChromaDB: {e}")
                
        return results

    def clear_document(self, document_name: str):
        """
        Removes all clauses belonging to a specific document.
        """
        if self.use_fallback:
            self.fallback_db = {vid: item for vid, item in self.fallback_db.items() if item["metadata"]["source_document"] != document_name}
        else:
            try:
                self.collection.delete(where={"source_document": document_name})
            except Exception as e:
                logger.error(f"Error deleting doc from ChromaDB: {e}")
