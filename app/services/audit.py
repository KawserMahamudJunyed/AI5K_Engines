"""Mock audit logging service for local development."""
import json
import uuid
from datetime import datetime, timezone
from typing import Any

__all__ = ["write_audit_log"]

async def write_audit_log(actor_id: uuid.UUID, action: str, entity_type: str, entity_id: uuid.UUID, metadata: dict[str, Any]) -> None:
    """Mock service that prints the audit trace to stdout in JSON format."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor_id": str(actor_id),
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "metadata": metadata,
    }
    print(f"[AUDIT] {json.dumps(log_entry)}")
