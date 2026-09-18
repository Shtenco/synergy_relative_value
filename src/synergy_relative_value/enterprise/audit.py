from __future__ import annotations

from collections import deque
from threading import RLock
from typing import Protocol
import json
from urllib.parse import urlparse

from .models import AuditEvent


class AuditStore(Protocol):
    def append(self, event: AuditEvent) -> None: ...
    def query(self, tenant_id: str, *, limit: int = 100) -> list[AuditEvent]: ...


class InMemoryAuditStore:
    def __init__(self, max_events: int = 10_000) -> None:
        self._events: deque[AuditEvent] = deque(maxlen=max_events)
        self._lock = RLock()

    def append(self, event: AuditEvent) -> None:
        with self._lock:
            self._events.append(event)

    def query(self, tenant_id: str, *, limit: int = 100) -> list[AuditEvent]:
        with self._lock:
            rows = [e for e in reversed(self._events) if e.tenant_id == tenant_id]
        return rows[: max(0, limit)]


class CompositeAuditStore:
    def __init__(self, stores: list[AuditStore], *, fail_closed: bool = True) -> None:
        if not stores:
            raise ValueError("at least one audit store is required")
        self.stores = list(stores)
        self.fail_closed = fail_closed

    def append(self, event: AuditEvent) -> None:
        errors: list[Exception] = []
        for store in self.stores:
            try:
                store.append(event)
            except Exception as exc:  # fail closed by default; never silently lose audit data
                errors.append(exc)
        if errors and self.fail_closed:
            raise RuntimeError(f"audit append failed in {len(errors)} store(s)") from errors[0]

    def query(self, tenant_id: str, *, limit: int = 100) -> list[AuditEvent]:
        return self.stores[0].query(tenant_id, limit=limit)


class PostgresAuditStore:
    def __init__(self, dsn: str, table: str = "audit_events") -> None:
        self.dsn = dsn
        self.table = table

    def append(self, event: AuditEvent) -> None:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("install psycopg[binary] to use PostgresAuditStore") from exc
        sql = f"INSERT INTO {self.table} (event_id, ts, tenant_id, actor, action, request_id, payload) VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)"
        values = (
            event.event_id,
            event.timestamp,
            event.tenant_id,
            event.actor,
            event.action,
            event.request_id,
            json.dumps(dict(event.payload), separators=(",", ":")),
        )
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)

    def query(self, tenant_id: str, *, limit: int = 100) -> list[AuditEvent]:
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("install psycopg[binary] to use PostgresAuditStore") from exc
        sql = f"SELECT event_id, ts, tenant_id, actor, action, request_id, payload FROM {self.table} WHERE tenant_id=%s ORDER BY ts DESC LIMIT %s"
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (tenant_id, max(0, limit)))
                rows = cur.fetchall()
        return [AuditEvent(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]


class ClickHouseAuditStore:
    def __init__(self, dsn: str, table: str = "audit_events", client=None) -> None:
        self.dsn = dsn
        self.table = table
        self._client = client

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import clickhouse_connect
        except ImportError as exc:
            raise RuntimeError("install clickhouse-connect to use ClickHouseAuditStore") from exc
        u = urlparse(self.dsn)
        self._client = clickhouse_connect.get_client(
            host=u.hostname or "localhost",
            port=u.port or (8443 if u.scheme == "https" else 8123),
            username=u.username or "default",
            password=u.password or "",
            database=(u.path or "/default").lstrip("/"),
            secure=u.scheme == "https",
        )
        return self._client

    def append(self, event: AuditEvent) -> None:
        client = self._get_client()
        client.insert(
            self.table,
            [[event.event_id, event.timestamp, event.tenant_id, event.actor, event.action, event.request_id, json.dumps(dict(event.payload), separators=(",", ":"))]],
            column_names=["event_id", "ts", "tenant_id", "actor", "action", "request_id", "payload"],
        )

    def query(self, tenant_id: str, *, limit: int = 100) -> list[AuditEvent]:
        client = self._get_client()
        safe_limit = max(0, min(int(limit), 10_000))
        result = client.query(
            f"SELECT event_id, ts, tenant_id, actor, action, request_id, payload FROM {self.table} WHERE tenant_id = {{tenant:String}} ORDER BY ts DESC LIMIT {safe_limit}",
            parameters={"tenant": tenant_id},
        )
        out = []
        for row in result.result_rows:
            payload = json.loads(row[6]) if isinstance(row[6], str) else row[6]
            out.append(AuditEvent(row[0], row[1], row[2], row[3], row[4], row[5], payload))
        return out
