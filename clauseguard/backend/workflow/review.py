import logging
from datetime import datetime
import json
from backend.db.database import ContradictionDB, ActiveLearningLabelDB, AuditLogDB
from backend.workflow.audit import log_audit_action

logger = logging.getLogger("ClauseGuardWorkflowReview")

def accept_contradiction(db_session, contradiction_id: int, reviewer_id: str) -> dict:
    """
    Accepts a flagged contradiction as a valid conflict.
    Saves a positive training label for the active learning engine.
    """
    contra = db_session.query(ContradictionDB).filter(ContradictionDB.id == contradiction_id).first()
    if not contra:
        raise ValueError(f"Contradiction ID {contradiction_id} not found.")
        
    contra.status = "accepted"
    
    # Store positive training example
    label_entry = ActiveLearningLabelDB(
        clause_a_text=contra.clause_a.text,
        clause_b_text=contra.clause_b.text,
        cosine_similarity=float(contra.final_confidence * 0.8),  # Simulated approximation
        llm_confidence=contra.llm_confidence,
        historical_frequency=0.5,
        label=1  # 1 = True positive
    )
    db_session.add(label_entry)
    db_session.commit()
    
    log_audit_action(db_session, "accept", reviewer_id, {
        "contradiction_id": contradiction_id,
        "clause_a": contra.clause_a.text[:60],
        "clause_b": contra.clause_b.text[:60],
        "severity": contra.severity
    })
    
    logger.info(f"Contradiction {contradiction_id} successfully accepted by reviewer {reviewer_id}.")
    return {"status": "success", "message": "Contradiction accepted successfully."}

def dismiss_contradiction(db_session, contradiction_id: int, reviewer_id: str, reason: str) -> dict:
    """
    Dismisses a flagged contradiction as a false positive.
    Saves a negative training label for the active learning engine.
    """
    contra = db_session.query(ContradictionDB).filter(ContradictionDB.id == contradiction_id).first()
    if not contra:
        raise ValueError(f"Contradiction ID {contradiction_id} not found.")
        
    contra.status = "dismissed"
    contra.dismissed_reason = reason
    
    # Store negative training example
    label_entry = ActiveLearningLabelDB(
        clause_a_text=contra.clause_a.text,
        clause_b_text=contra.clause_b.text,
        cosine_similarity=float(contra.final_confidence * 0.8),
        llm_confidence=contra.llm_confidence,
        historical_frequency=0.5,
        label=0  # 0 = False positive
    )
    db_session.add(label_entry)
    db_session.commit()
    
    log_audit_action(db_session, "dismiss", reviewer_id, {
        "contradiction_id": contradiction_id,
        "reason": reason
    })
    
    logger.info(f"Contradiction {contradiction_id} successfully dismissed by reviewer {reviewer_id}.")
    return {"status": "success", "message": "Contradiction dismissed successfully."}

def escalate_contradiction(db_session, contradiction_id: int, reviewer_id: str, note: str) -> dict:
    """
    Escalates a flagged contradiction to global compliance officer queue.
    Emit notifications via Websocket.
    """
    contra = db_session.query(ContradictionDB).filter(ContradictionDB.id == contradiction_id).first()
    if not contra:
        raise ValueError(f"Contradiction ID {contradiction_id} not found.")
        
    contra.status = "escalated"
    db_session.commit()
    
    log_audit_action(db_session, "escalate", reviewer_id, {
        "contradiction_id": contradiction_id,
        "escalation_note": note
    })
    
    logger.info(f"Contradiction {contradiction_id} successfully escalated by reviewer {reviewer_id}.")
    return {"status": "success", "message": "Contradiction escalated successfully."}
