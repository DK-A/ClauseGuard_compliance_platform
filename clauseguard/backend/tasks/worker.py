import logging
import threading
import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.database import DBConfig, DocumentDB, ClauseDB, ContradictionDB
from backend.ingestion.parser import parse_document
from backend.ingestion.chunker import chunk_document
from backend.retrieval.vectorstore import VectorStore
from backend.retrieval.two_tower import TwoTowerRetrieval
from backend.reasoning.chain import ContradictionReasonerChain
from backend.reasoning.confidence import ConfidenceCalibrator

logger = logging.getLogger("ClauseGuardWorker")

class AnalysisWorker:
    def __init__(self):
        self.vector_store = VectorStore()
        self.two_tower = TwoTowerRetrieval()
        self.reasoner = ContradictionReasonerChain()
        self.calibrator = ConfidenceCalibrator()

    def run_analysis_async(self, document_ids: list, session_id: str, ws_broadcast_func=None):
        """
        Spawns a background thread to process text ingestion and legal semantic comparison.
        """
        thread = threading.Thread(
            target=self._process_pipeline,
            args=(document_ids, session_id, ws_broadcast_func)
        )
        thread.daemon = True
        thread.start()
        logger.info(f"Spawned background analysis pipeline thread for session {session_id}.")

    def _process_pipeline(self, document_ids: list, session_id: str, ws_broadcast_func=None):
        db: Session = DBConfig.SessionLocal()
        try:
            logger.info(f"Starting ingestion pipeline for session {session_id}...")
            
            # Fetch documents
            docs = db.query(DocumentDB).filter(DocumentDB.id.in_(document_ids)).all()
            for doc in docs:
                doc.status = "parsing"
            db.commit()
            
            all_clauses = []
            
            # Ingest, Parse, and Chunk each document
            for doc in docs:
                try:
                    logger.info(f"Parsing document: {doc.filename}...")
                    parsed_pages = parse_document(doc.filepath)
                    
                    logger.info(f"Chunking document sentences: {doc.filename}...")
                    clauses_data = chunk_document(parsed_pages, doc.filename)
                    
                    db_clauses = []
                    for c in clauses_data:
                        summary_val = summarize_clause_text(self.reasoner, c["text"])
                        db_clause = ClauseDB(
                            text=c["text"],
                            document_id=doc.id,
                            clause_type=c["clause_type"],
                            named_entities=json_dumps_safe(c["named_entities"]),
                            section_heading=c["section_heading"],
                            page_number=c["page_number"],
                            vector_id=c["vector_id"],
                            summary=summary_val
                        )
                        db.add(db_clause)
                        db_clauses.append(db_clause)
                        
                    db.commit()
                    
                    # Push to vector store
                    self.vector_store.add_clauses(clauses_data, doc.filename)
                    
                    # Store locally mapped reference dict for two-tower retrieval
                    for c_idx, c_obj in enumerate(clauses_data):
                        c_obj["id"] = db_clauses[c_idx].id
                        c_obj["source_document"] = doc.filename
                        all_clauses.append(c_obj)
                        
                    doc.status = "parsed"
                    db.commit()
                except Exception as e:
                    doc.status = "error"
                    db.commit()
                    logger.error(f"Failed parsing document {doc.filename}: {e}", exc_info=True)
                    continue

            # Run Two-Tower Comparison & Reasoning
            logger.info("Executing global Two-Tower comparison & reasoning...")
            found_conflicts_count = 0
            
            # Keep track of compared pairs to avoid duplicate A-B and B-A checks
            compared_pairs = set()
            
            for clause in all_clauses:
                clause_id = clause["id"]
                candidates = self.two_tower.find_contradiction_candidates(clause, all_clauses)
                
                for candidate in candidates:
                    match = candidate["b"] if "b" in candidate else candidate["clause_b"]
                    match_id = match.get("id")
                    if match_id is None:
                        match_vector_id = match.get("vector_id")
                        match_db_clause = db.query(ClauseDB).filter(ClauseDB.vector_id == match_vector_id).first()
                        if match_db_clause:
                            match_id = match_db_clause.id
                        else:
                            logger.warning(f"Could not find clause in DB with vector_id {match_vector_id}")
                            continue
                    
                    # Make symmetrical pair tuple
                    pair_key = tuple(sorted([clause_id, match_id]))
                    if pair_key in compared_pairs:
                        continue
                    compared_pairs.add(pair_key)
                    
                    # Run Multi-Step Reasoning
                    logger.info(f"Comparing Clause {clause_id} vs Clause {match_id}...")
                    analysis = self.reasoner.analyze_pair(clause["text"], match["text"])
                    relationship = analysis.get("relationship", "NO_CONFLICT")
                    
                    if relationship != "NO_CONFLICT":
                        # Compute final calibrated confidence score
                        cosine_sim = candidate["cosine_similarity"]
                        llm_conf = analysis.get("llm_confidence", 0.85)
                        
                        final_conf = self.calibrator.calculate_score(
                            cosine_sim=cosine_sim,
                            llm_conf=llm_conf,
                            historical_freq=0.5
                        )
                        
                        # Store contradiction record in SQLite DB
                        contradiction = ContradictionDB(
                            clause_a_id=clause_id,
                            clause_b_id=match_id,
                            relationship=relationship,
                            business_risk=analysis.get("business_risk", ""),
                            severity=analysis.get("severity", "HIGH"),
                            recommended_resolution=analysis.get("recommended_resolution", ""),
                            llm_confidence=llm_conf,
                            final_confidence=final_conf,
                            status="open"
                        )
                        db.add(contradiction)
                        found_conflicts_count += 1
                        
            db.commit()
            
            # Finalize documents status
            for doc in docs:
                if doc.status == "parsed":
                    doc.status = "completed"
            db.commit()
            
            logger.info(f"Ingestion analysis complete! Flagged {found_conflicts_count} contradictions across documents.")
            
            # Broadcast WebSocket updates
            if ws_broadcast_func:
                try:
                    ws_broadcast_func({
                        "event": "ANALYSIS_COMPLETE",
                        "session_id": session_id,
                        "conflicts_count": found_conflicts_count,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Critical error in background analysis pipeline: {e}", exc_info=True)
        finally:
            db.close()

def json_dumps_safe(obj) -> str:
    try:
        return json.dumps(obj)
    except Exception:
        return "{}"

def summarize_clause_text(reasoner, text: str) -> str:
    prompt = f"Summarize this legal clause in 10-15 words focusing strictly on timelines or obligations: {text}"
    try:
        summary = reasoner._invoke_llm(prompt).strip()
        summary = summary.replace('"', '').replace("'", "").strip()
        if len(summary) > 100:
            summary = summary[:97] + "..."
        return summary
    except Exception:
        return text[:75] + "..."
