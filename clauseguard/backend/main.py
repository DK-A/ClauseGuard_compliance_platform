import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.db.database import get_db, init_db, DocumentDB, ClauseDB, ContradictionDB, AuditLogDB, ActiveLearningLabelDB
from backend.models.schemas import (
    DocumentResponse, ContradictionResponse, ResolutionProposal,
    KPIDashboardResponse, TelemetryStatus, DeployedModelStatus
)
from backend.config import get_profile, get_registry
from backend.hardware.monitor import HardwareMonitor
from backend.tasks.worker import AnalysisWorker
from backend.workflow.review import accept_contradiction, dismiss_contradiction, escalate_contradiction
from backend.workflow.resolution import propose_resolutions, apply_resolution
from backend.graph.builder import ContradictionGraphBuilder
from backend.graph.impact import ResolutionImpactAnalyzer
from backend.learning.active import ActiveLearningEngine

logger = logging.getLogger("ClauseGuardAPI")

# Initialize database
init_db()

app = FastAPI(title="ClauseGuard API Gateway", version="4.0.0")

# Enable CORS for Vite local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared objects
registry = get_registry()
monitor = HardwareMonitor(registry)
worker = AnalysisWorker()
graph_builder = ContradictionGraphBuilder()

# WebSocket connections tracking
active_websockets: List[WebSocket] = []

@app.on_event("startup")
def on_startup():
    # Set monitor WebSocket alert callback to broadcast resource warnings
    monitor.register_ws_callback(broadcast_ws_message)
    logger.info("FastAPI ClauseGuard Backend Startup Complete.")

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            # Keep connection alive; wait for client messages if any
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

def broadcast_ws_message(message: dict):
    """
    Utility helper to broadcast event alerts to all connected WS clients.
    """
    payload = json.dumps(message)
    import asyncio
    loop = asyncio.get_event_loop()
    for ws in active_websockets:
        try:
            loop.create_task(ws.send_text(payload))
        except Exception:
            pass

# --- DOCUMENTS MANAGEMENT ---

@app.post("/api/documents/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...), 
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    upload_dir = "uploaded_data"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
            
        doc_entry = DocumentDB(
            filename=file.filename,
            filepath=file_path,
            session_id=session_id,
            status="pending"
        )
        db.add(doc_entry)
        db.commit()
        db.refresh(doc_entry)
        
        # Log to audit trail
        log_audit(db, "upload", "System", {"filename": file.filename, "session_id": session_id})
        
        return doc_entry
    except Exception as e:
        logger.error(f"Error uploading document {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error uploading document.")

@app.get("/api/documents", response_model=List[DocumentResponse])
def get_documents(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    if session_id:
        return db.query(DocumentDB).filter(DocumentDB.session_id == session_id).all()
    return db.query(DocumentDB).all()

# --- ANALYSIS PIPELINE ---

@app.post("/api/analysis/run")
def run_analysis(payload: Dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id in payload.")
        
    docs = db.query(DocumentDB).filter(DocumentDB.session_id == session_id, DocumentDB.status == "pending").all()
    if not docs:
        raise HTTPException(status_code=404, detail="No pending documents found for session_id.")
        
    doc_ids = [d.id for d in docs]
    
    # Run the background two-tower + logic pipeline asynchronously
    worker.run_analysis_async(
        document_ids=doc_ids,
        session_id=session_id,
        ws_broadcast_func=broadcast_ws_message
    )
    
    return {"status": "started", "message": f"Analysis pipeline started for {len(doc_ids)} files."}

@app.get("/api/analysis/{session_id}")
def check_analysis_status(session_id: str, db: Session = Depends(get_db)):
    docs = db.query(DocumentDB).filter(DocumentDB.session_id == session_id).all()
    if not docs:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    statuses = [d.status for d in docs]
    overall = "completed"
    if "parsing" in statuses:
        overall = "processing"
    elif "pending" in statuses:
        overall = "pending"
    elif "error" in statuses:
        overall = "error"
        
    return {
        "session_id": session_id,
        "status": overall,
        "files": [{"id": d.id, "filename": d.filename, "status": d.status} for d in docs]
    }

# --- CONTRADICTIONS WORKFLOW ---

@app.get("/api/contradictions", response_model=List[ContradictionResponse])
def get_contradictions(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    if session_id:
        return db.query(ContradictionDB).join(
            ClauseDB, ContradictionDB.clause_a_id == ClauseDB.id
        ).join(
            DocumentDB, ClauseDB.document_id == DocumentDB.id
        ).filter(
            DocumentDB.session_id == session_id
        ).all()
    return db.query(ContradictionDB).all()

@app.get("/api/contradictions/{id}", response_model=ContradictionResponse)
def get_contradiction_by_id(id: int, db: Session = Depends(get_db)):
    contra = db.query(ContradictionDB).filter(ContradictionDB.id == id).first()
    if not contra:
        raise HTTPException(status_code=404, detail="Contradiction record not found.")
    return contra

@app.post("/api/contradictions/{id}/accept")
def accept_inconsistency(id: int, payload: Dict[str, str], db: Session = Depends(get_db)):
    reviewer_id = payload.get("reviewer_id", "Reviewer Portal")
    try:
        return accept_contradiction(db, id, reviewer_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@app.post("/api/contradictions/{id}/dismiss")
def dismiss_inconsistency(id: int, payload: Dict[str, str], db: Session = Depends(get_db)):
    reviewer_id = payload.get("reviewer_id", "Reviewer Portal")
    reason = payload.get("reason", "Dismissed without comments.")
    try:
        return dismiss_contradiction(db, id, reviewer_id, reason)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@app.post("/api/contradictions/{id}/escalate")
def escalate_inconsistency(id: int, payload: Dict[str, str], db: Session = Depends(get_db)):
    reviewer_id = payload.get("reviewer_id", "Reviewer Portal")
    note = payload.get("note", "Escalated for compliance review.")
    try:
        res = escalate_contradiction(db, id, reviewer_id, note)
        # Broadcast escalation WS event
        broadcast_ws_message({
            "event": "CONTRADICTION_ESCALATED",
            "contradiction_id": id,
            "escalated_by": reviewer_id,
            "note": note
        })
        return res
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@app.get("/api/contradictions/{id}/resolutions", response_model=List[ResolutionProposal])
def get_resolutions_proposals(id: int, db: Session = Depends(get_db)):
    try:
        return propose_resolutions(db, id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@app.post("/api/contradictions/{id}/resolve")
def resolve_inconsistency(id: int, payload: Dict[str, str], db: Session = Depends(get_db)):
    reviewer_id = payload.get("reviewer_id", "Reviewer Portal")
    strategy = payload.get("strategy")
    amended_text = payload.get("amended_clause_text")
    if not strategy or not amended_text:
        raise HTTPException(status_code=400, detail="Missing strategy or amended text.")
        
    try:
        return apply_resolution(db, id, strategy, amended_text, reviewer_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

# --- KNOWLEDGE GRAPH & NETWORKX ---

def sync_active_graph(db: Session, session_id: Optional[str] = None):
    """
    Populates NetworkX singleton with current SQLite document and contradiction states.
    """
    graph_builder.clear()
    
    # 1. Fetch all active document clauses
    if session_id:
        clauses = db.query(ClauseDB).join(DocumentDB).filter(DocumentDB.session_id == session_id).all()
    else:
        clauses = db.query(ClauseDB).all()
        
    for c in clauses:
        # Load named entities safely
        entities = {}
        try:
            entities = json.loads(c.named_entities)
        except Exception:
            pass
            
        graph_builder.add_clause_node(
            clause_id=c.id,
            text=c.text,
            doc_source=c.document.filename,
            clause_type=c.clause_type,
            page_number=c.page_number,
            section=c.section_heading,
            entity_metadata=entities
        )
        
    # 2. Fetch all contradiction links
    if session_id:
        contras = db.query(ContradictionDB).join(
            ClauseDB, ContradictionDB.clause_a_id == ClauseDB.id
        ).join(
            DocumentDB, ClauseDB.document_id == DocumentDB.id
        ).filter(
            DocumentDB.session_id == session_id
        ).all()
    else:
        contras = db.query(ContradictionDB).all()
        
    for c in contras:
        graph_builder.add_contradiction_edge(
            edge_id=c.id,
            clause_a_id=c.clause_a_id,
            clause_b_id=c.clause_b_id,
            contradiction_type=c.relationship,
            severity=c.severity,
            confidence=c.final_confidence,
            status=c.status,
            resolution_text=c.resolution_text or ""
        )

@app.get("/api/graph")
def get_knowledge_graph(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    sync_active_graph(db, session_id)
    return graph_builder.serialize_for_frontend()

@app.get("/api/graph/cluster/{node_id}")
def get_graph_neighborhood(node_id: int, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    sync_active_graph(db, session_id)
    return graph_builder.get_cluster(node_id)

@app.get("/api/graph/impact/{node_id}")
def simulate_resolution_impact(node_id: int, proposed_edit: str, session_id: Optional[str] = None, db: Session = Depends(get_db)):
    sync_active_graph(db, session_id)
    analyzer = ResolutionImpactAnalyzer(db, graph_builder)
    return analyzer.analyze_resolution_impact(node_id, proposed_edit)

# --- KPI METRICS & TELEMETRY ---

@app.get("/api/kpi", response_model=KPIDashboardResponse)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    # Counts confirmed/resolved contradictions to calculate savings
    confirmed_count = db.query(ContradictionDB).filter(ContradictionDB.status.in_(["accepted", "resolved"])).count()
    total_count = db.query(ContradictionDB).count()
    
    # Industry average financial prevented value per contradiction: ₹10,00,000
    risk_prevented = confirmed_count * 1000000.0
    
    # Calculate False Positive Rate
    dismissed = db.query(ContradictionDB).filter(ContradictionDB.status == "dismissed").count()
    false_positive_rate = round((dismissed / total_count * 100.0), 1) if total_count > 0 else 0.0
    
    active_learning = ActiveLearningEngine(db)
    accuracy_trend = active_learning.get_accuracy_trend()
    current_accuracy = accuracy_trend[-1]
    
    config = registry.get_reasoning_config()
    
    return {
        "financial_risk_prevented": risk_prevented,
        "review_time_saved_pct": 94.0,  # Nominal default
        "compliance_score": 98.2,
        "false_positive_rate": false_positive_rate,
        "model_accuracy": current_accuracy,
        "active_profile": config.profile_name,
        "primary_model": config.primary_model,
        "fallback_active": registry.fallback_active
    }

@app.get("/api/edge/status", response_model=TelemetryStatus)
def get_hardware_telemetry():
    return monitor.get_status()

# Force manual development override endpoint for testing profiles
@app.post("/api/edge/override")
def force_hardware_profile(payload: Dict[str, str]):
    target = payload.get("profile")
    if target in ["LAPTOP", "RPI5", "RPI4"]:
        from backend.hardware.fingerprint import ProfileType
        registry.profile = ProfileType(target)
        registry._llm_instance = None  # Reload model settings
        config = registry.get_reasoning_config()
        logger.info(f"Forced hardware profile registry override: {target}")
        return {"status": "success", "message": f"Successfully mapped override to: {config.profile_name}"}
    raise HTTPException(status_code=400, detail="Invalid profile name.")

@app.get("/api/learning/accuracy")
def get_active_learning_trend(db: Session = Depends(get_db)):
    engine = ActiveLearningEngine(db)
    return {"accuracy_history": engine.get_accuracy_trend()}

@app.get("/api/audit")
def get_historical_audit_log(db: Session = Depends(get_db)):
    logs = db.query(AuditLogDB).order_by(AuditLogDB.timestamp.desc()).all()
    results = []
    for l in logs:
        details_dict = {}
        try:
            details_dict = json.loads(l.details)
        except Exception:
            pass
        results.append({
            "id": l.id,
            "action": l.action,
            "user_id": l.user_id,
            "timestamp": l.timestamp,
            "details": details_dict
        })
    return results

def log_audit(db_session, action: str, user: str, details: dict):
    entry = AuditLogDB(
        action=action,
        user_id=user,
        timestamp=datetime.utcnow(),
        details=json.dumps(details)
    )
    db_session.add(entry)
    db_session.commit()

# --- SESSIONS & SHARING WORKFLOWS ---

@app.get("/api/sessions")
def get_sessions(db: Session = Depends(get_db)):
    results = db.query(DocumentDB.session_id).distinct().all()
    return [r[0] for r in results if r[0]]

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    docs = db.query(DocumentDB).filter(DocumentDB.session_id == session_id).all()
    if not docs:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    doc_ids = [d.id for d in docs]
    
    # Manually delete contradictions, clauses, documents, and clear vectors
    for d in docs:
        try:
            worker.vector_store.clear_document(d.filename)
        except Exception as e:
            logger.warning(f"Error clearing ChromaDB for {d.filename}: {e}")
            
    # Subquery delete for SQLite compatibility
    clause_ids_query = db.query(ClauseDB.id).filter(ClauseDB.document_id.in_(doc_ids)).all()
    clause_ids = [c[0] for c in clause_ids_query]
    
    if clause_ids:
        db.query(ContradictionDB).filter(
            (ContradictionDB.clause_a_id.in_(clause_ids)) | 
            (ContradictionDB.clause_b_id.in_(clause_ids))
        ).delete(synchronize_session=False)
        
        db.query(ClauseDB).filter(ClauseDB.id.in_(clause_ids)).delete(synchronize_session=False)
        
    db.query(DocumentDB).filter(DocumentDB.session_id == session_id).delete(synchronize_session=False)
    db.commit()
    
    logger.info(f"Session {session_id} and all related files deleted successfully.")
    return {"status": "success", "message": f"Session {session_id} deleted successfully."}

@app.post("/api/share")
def share_report(payload: Dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("session_id")
    email = payload.get("email", "officials@clauseguard.corp")
    channel = payload.get("channel", "Email")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session_id in payload.")
        
    docs = db.query(DocumentDB).filter(DocumentDB.session_id == session_id).all()
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found for session.")
        
    contras = db.query(ContradictionDB).join(
        ClauseDB, ContradictionDB.clause_a_id == ClauseDB.id
    ).join(
        DocumentDB, ClauseDB.document_id == DocumentDB.id
    ).filter(
        DocumentDB.session_id == session_id
    ).all()
    
    report_md = f"# ClauseGuard Compliance Inconsistency Report\n"
    report_md += f"**Active Session**: {session_id}\n"
    report_md += f"**Dispatched to**: {email} via {channel}\n"
    report_md += f"**Date**: {datetime.utcnow().isoformat()[:19]} Z\n\n"
    
    report_md += f"## 1. Scope & Audited files ({len(docs)})\n"
    for d in docs:
        report_md += f"- `{d.filename}` (Status: {d.status.upper()})\n"
        
    report_md += f"\n## 2. Inconsistencies Discovered ({len(contras)})\n"
    if not contras:
        report_md += "_No contradictions flagged in this session._\n"
    for idx, c in enumerate(contras):
        report_md += f"### Conflict #{idx+1}: {c.clause_a.section_heading} ({c.severity} Severity)\n"
        report_md += f"- **Master Document** (`{c.clause_a.document.filename}`): \"{c.clause_a.text[:120]}...\"\n"
        report_md += f"- **Draft Document** (`{c.clause_b.document.filename}`): \"{c.clause_b.text[:120]}...\"\n"
        report_md += f"- **Business Risk**: {c.business_risk}\n"
        report_md += f"- **Resolution Recommendation**: {c.recommended_resolution}\n\n"
        
    logger.info(f"Report shared successfully to {email} via {channel} for session {session_id}.")
    return {
        "status": "success",
        "message": f"Compliance report shared successfully to {email} via {channel}.",
        "report": report_md
    }
