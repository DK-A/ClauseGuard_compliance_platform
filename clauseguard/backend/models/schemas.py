from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

class DocumentBase(BaseModel):
    filename: str
    filepath: str
    session_id: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    uploaded_at: datetime
    status: str

    class Config:
        from_attributes = True

class ClauseBase(BaseModel):
    text: str
    clause_type: str
    named_entities: Dict[str, List[str]]
    section_heading: str
    page_number: int
    vector_id: str
    source_document: Optional[str] = None
    summary: Optional[str] = None

    @field_validator('named_entities', mode='before')
    @classmethod
    def deserialize_named_entities(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v

class ClauseCreate(ClauseBase):
    document_id: int

class ClauseResponse(ClauseBase):
    id: int
    document_id: int

    class Config:
        from_attributes = True

class ContradictionBase(BaseModel):
    relationship: str
    business_risk: str
    severity: str
    recommended_resolution: str
    llm_confidence: float
    final_confidence: float
    status: str

class ContradictionResponse(BaseModel):
    id: int
    clause_a: ClauseResponse
    clause_b: ClauseResponse
    relationship: str
    business_risk: str
    severity: str
    recommended_resolution: str
    llm_confidence: float
    final_confidence: float
    status: str
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_text: Optional[str] = None
    dismissed_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResolutionProposal(BaseModel):
    strategy: str
    amended_clause_text: str
    confidence: float

class AuditLogResponse(BaseModel):
    id: int
    action: str
    user_id: str
    timestamp: datetime
    details: Dict[str, Any]

    class Config:
        from_attributes = True

class DeployedModelStatus(BaseModel):
    name: str
    status: str  # ACTIVE or STANDBY
    parameters: str
    quantization: str
    memory_usage: str
    latency: str

class TelemetryStatus(BaseModel):
    cpu_pct: float
    ram_pct: float
    temperature_c: float
    current_tps: float
    active_model: str
    fallback_model: str
    profile_name: str
    fallback_active: bool
    hardware_integrity: Dict[str, str]
    deployed_models: List[DeployedModelStatus]
    simulated: bool = False

class KPIDashboardResponse(BaseModel):
    financial_risk_prevented: float
    review_time_saved_pct: float
    compliance_score: float
    false_positive_rate: float
    model_accuracy: float
    active_profile: str
    primary_model: str
    fallback_active: bool
