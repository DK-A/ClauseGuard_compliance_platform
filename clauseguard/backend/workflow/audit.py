import json
from datetime import datetime
from backend.db.database import AuditLogDB

def log_audit_action(db_session, action: str, user_id: str, details: dict):
    """
    Saves a serialized, timestamped record of human administrative actions.
    """
    log_entry = AuditLogDB(
        action=action,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        details=json.dumps(details)
    )
    db_session.add(log_entry)
    db_session.commit()
