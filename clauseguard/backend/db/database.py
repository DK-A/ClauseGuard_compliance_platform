import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship as sa_relationship

Base = declarative_base()

class DBConfig:
    DB_PATH = os.environ.get("DB_PATH", "clauseguard.db")
    ENGINE = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

class DocumentDB(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, parsed, completed, error
    session_id = Column(String, index=True)

class ClauseDB(Base):
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    clause_type = Column(String)  # obligation, prohibition, permission, definition, exception
    named_entities = Column(Text)  # JSON string
    section_heading = Column(String)
    page_number = Column(Integer)
    vector_id = Column(String, unique=True, index=True)
    summary = Column(Text, nullable=True)
    
    document = sa_relationship("DocumentDB", backref="clauses")

    @property
    def source_document(self) -> str:
        return self.document.filename if self.document else ""

class ContradictionDB(Base):
    __tablename__ = "contradictions"
    
    id = Column(Integer, primary_key=True, index=True)
    clause_a_id = Column(Integer, ForeignKey("clauses.id", ondelete="CASCADE"))
    clause_b_id = Column(Integer, ForeignKey("clauses.id", ondelete="CASCADE"))
    relationship = Column(String)  # DIRECT_CONTRADICTION, PARTIAL_OVERLAP, AMBIGUITY, SUPERSESSION, NO_CONFLICT
    business_risk = Column(Text)
    severity = Column(String)  # CRITICAL, HIGH, MEDIUM, LOW
    recommended_resolution = Column(Text)
    llm_confidence = Column(Float)
    final_confidence = Column(Float)
    status = Column(String, default="open")  # open, resolved, dismissed, escalated
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_text = Column(Text, nullable=True)
    dismissed_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    clause_a = sa_relationship("ClauseDB", foreign_keys=[clause_a_id], backref="contradictions_a")
    clause_b = sa_relationship("ClauseDB", foreign_keys=[clause_b_id], backref="contradictions_b")

class ActiveLearningLabelDB(Base):
    __tablename__ = "active_learning_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    clause_a_text = Column(Text)
    clause_b_text = Column(Text)
    cosine_similarity = Column(Float)
    llm_confidence = Column(Float)
    historical_frequency = Column(Float)
    label = Column(Integer)  # 1 = true contradiction, 0 = false positive
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLogDB(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)  # upload, accept, dismiss, resolve, escalate
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)  # JSON string

def get_db():
    db = DBConfig.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=DBConfig.ENGINE)
