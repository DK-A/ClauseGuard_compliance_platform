import logging
from datetime import datetime
from backend.db.database import ContradictionDB, ClauseDB
from backend.config import get_llm
from backend.workflow.audit import log_audit_action

logger = logging.getLogger("ClauseGuardWorkflowResolution")

def propose_resolutions(db_session, contradiction_id: int) -> list:
    """
    Generates three structured legal resolution strategies using the active LLM:
    1. Keep Clause A / Amend Clause B
    2. Keep Clause B / Amend Clause A
    3. Draft new harmonized clause blending both parameters safely.
    """
    contra = db_session.query(ContradictionDB).filter(ContradictionDB.id == contradiction_id).first()
    if not contra:
        raise ValueError(f"Contradiction ID {contradiction_id} not found.")
        
    clause_a = contra.clause_a.text
    clause_b = contra.clause_b.text
    
    llm = get_llm()
    
    prompt = f"""
    You are an expert corporate legal counsel.
    Analyze this contradiction between two organizational clauses:
    
    Clause A: {clause_a}
    Clause B: {clause_b}
    
    In plain legal terminology, draft three options to resolve this contradiction:
    1. Strategy: Keep Clause A / Amend Clause B. Draft the exact amended text for Clause B so it aligns with Clause A without creating new liability risks.
    2. Strategy: Keep Clause B / Amend Clause A. Draft the exact amended text for Clause A.
    3. Strategy: Harmonize both. Draft a single combined clause that blends the terms safely and mutually protects the organization.
    
    Respond in exactly this JSON list format and nothing else. No prose or introductory text:
    [
      {{"strategy": "Amend Clause B", "amended_clause_text": "[Amended text here]", "confidence": 0.95}},
      {{"strategy": "Amend Clause A", "amended_clause_text": "[Amended text here]", "confidence": 0.90}},
      {{"strategy": "Harmonize Both", "amended_clause_text": "[Harmonized text here]", "confidence": 0.85}}
    ]
    """
    
    try:
        response = llm.invoke(prompt).content
        # Simple extraction of JSON lists
        import re
        import json
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            proposals = json.loads(json_match.group(0))
            return proposals
    except Exception as e:
        logger.error(f"Error generating resolutions from LLM: {e}. Executing template fallback.")
        
    # Standard template fallback resolutions
    return [
        {
            "strategy": "Amend Clause B", 
            "amended_clause_text": f"{clause_a} (Amended to conform to master terms)", 
            "confidence": 0.95
        },
        {
            "strategy": "Amend Clause A", 
            "amended_clause_text": f"{clause_b} (Amended to align with inbound specifications)", 
            "confidence": 0.90
        },
        {
            "strategy": "Harmonize Both", 
            "amended_clause_text": f"Both parties agree that: {clause_a} and {clause_b}. In case of operational inconsistencies, standard mutual protocols apply.", 
            "confidence": 0.85
        }
    ]

def apply_resolution(db_session, contradiction_id: int, strategy: str, amended_text: str, reviewer_id: str) -> dict:
    """
    Applies the chosen resolution strategy. Updates clause texts in the DB, sets status to 'resolved'.
    Logs the resolution in the audit trail.
    """
    contra = db_session.query(ContradictionDB).filter(ContradictionDB.id == contradiction_id).first()
    if not contra:
        raise ValueError(f"Contradiction ID {contradiction_id} not found.")
        
    # Apply text updates depending on strategy
    if "Amend Clause B" in strategy:
        db_clause = db_session.query(ClauseDB).filter(ClauseDB.id == contra.clause_b_id).first()
        if db_clause:
            db_clause.text = amended_text
    elif "Amend Clause A" in strategy:
        db_clause = db_session.query(ClauseDB).filter(ClauseDB.id == contra.clause_a_id).first()
        if db_clause:
            db_clause.text = amended_text
    elif "Harmonize" in strategy:
        # Update both
        db_clause_a = db_session.query(ClauseDB).filter(ClauseDB.id == contra.clause_a_id).first()
        db_clause_b = db_session.query(ClauseDB).filter(ClauseDB.id == contra.clause_b_id).first()
        if db_clause_a:
            db_clause_a.text = amended_text
        if db_clause_b:
            db_clause_b.text = amended_text

    contra.status = "resolved"
    contra.resolved_by = reviewer_id
    contra.resolved_at = datetime.utcnow()
    contra.resolution_text = amended_text
    
    db_session.commit()
    
    log_audit_action(db_session, "resolve", reviewer_id, {
        "contradiction_id": contradiction_id,
        "strategy": strategy,
        "amended_text": amended_text
    })
    
    logger.info(f"Contradiction {contradiction_id} successfully resolved using strategy '{strategy}' by {reviewer_id}.")
    return {"status": "success", "message": "Resolution applied successfully."}
