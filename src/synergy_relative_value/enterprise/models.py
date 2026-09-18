from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
import uuid


class Role(str, Enum):
    VIEWER = "viewer"
    RESEARCHER = "researcher"
    TRADER = "trader"
    RISK = "risk"
    OPERATOR = "operator"
    ADMIN = "admin"


@dataclass(frozen=True)
class Principal:
    subject: str
    roles: frozenset[Role]
    tenant_id: str = "default"
    token_id: str | None = None


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    timestamp: datetime
    tenant_id: str
    actor: str
    action: str
    request_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        tenant_id: str,
        actor: str,
        action: str,
        request_id: str,
        payload: Mapping[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> "AuditEvent":
        return cls(
            event_id=str(uuid.uuid4()),
            timestamp=timestamp or datetime.now(timezone.utc),
            tenant_id=tenant_id,
            actor=actor,
            action=action,
            request_id=request_id,
            payload=dict(payload or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "actor": self.actor,
            "action": self.action,
            "request_id": self.request_id,
            "payload": dict(self.payload),
        }
