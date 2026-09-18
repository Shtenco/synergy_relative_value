from __future__ import annotations

from dataclasses import dataclass, field
import os
import time
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .audit import ClickHouseAuditStore, CompositeAuditStore, InMemoryAuditStore, PostgresAuditStore
from .auth import AuthError, require_role, verify_token
from .metrics import MetricsRegistry
from .models import AuditEvent, Principal, Role

_bearer = HTTPBearer(auto_error=False)


@dataclass
class EnterpriseRuntime:
    service_name: str
    auth_secret: str
    audit_store: object = field(default_factory=InMemoryAuditStore)
    metrics: MetricsRegistry | None = None
    environment: str = "dev"
    started_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = MetricsRegistry(namespace=self.service_name)

    @classmethod
    def from_env(cls, *, service_name: str) -> "EnterpriseRuntime":
        environment = os.getenv("SYNERGY_ENV", "dev").lower()
        secret = os.getenv("SYNERGY_AUTH_SECRET")
        if not secret:
            if environment != "dev":
                raise RuntimeError("SYNERGY_AUTH_SECRET is required outside dev")
            secret = "dev-only-change-me-not-for-production"
        stores = []
        pg = os.getenv("SYNERGY_POSTGRES_DSN")
        ch = os.getenv("SYNERGY_CLICKHOUSE_DSN")
        if pg:
            stores.append(PostgresAuditStore(pg))
        if ch:
            stores.append(ClickHouseAuditStore(ch))
        audit = CompositeAuditStore(stores) if stores else InMemoryAuditStore()
        return cls(service_name=service_name, auth_secret=secret, audit_store=audit, environment=environment)

    def record(self, principal: Principal, *, action: str, request_id: str, payload: dict) -> AuditEvent:
        event = AuditEvent.create(tenant_id=principal.tenant_id, actor=principal.subject, action=action, request_id=request_id, payload=payload)
        self.audit_store.append(event)
        self.metrics.inc("audit_events_total", labels={"action": action})
        return event


def principal_dependency(runtime: EnterpriseRuntime, allowed: set[Role] | None = None):
    async def dep(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> Principal:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="bearer token required")
        try:
            principal = verify_token(credentials.credentials, runtime.auth_secret)
            if allowed is not None:
                require_role(principal, allowed)
            return principal
        except AuthError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
    return dep


def request_id_header(x_request_id: str | None = Header(default=None, alias="X-Request-ID")) -> str:
    return x_request_id or str(uuid.uuid4())


def build_enterprise_router(runtime: EnterpriseRuntime) -> APIRouter:
    router = APIRouter(prefix="/enterprise", tags=["enterprise-control"])

    @router.get("/health")
    async def health():
        runtime.metrics.inc("requests_total", labels={"route": "health"})
        return {
            "ok": True,
            "service": runtime.service_name,
            "environment": runtime.environment,
            "uptime_seconds": max(0.0, time.time() - runtime.started_at),
            "audit_store": type(runtime.audit_store).__name__,
        }

    @router.get("/metrics", response_class=PlainTextResponse)
    async def metrics():
        return runtime.metrics.render_prometheus()

    @router.get("/whoami")
    async def whoami(principal: Principal = Depends(principal_dependency(runtime))):
        return {"subject": principal.subject, "tenant_id": principal.tenant_id, "roles": sorted(r.value for r in principal.roles)}

    @router.get("/audit")
    async def audit(limit: int = 100, principal: Principal = Depends(principal_dependency(runtime, {Role.ADMIN}))):
        return [e.to_dict() for e in runtime.audit_store.query(principal.tenant_id, limit=min(max(limit, 1), 1000))]

    return router


def install_observability(app, runtime: EnterpriseRuntime) -> None:
    """Attach request-id propagation and dependency-free Prometheus-style latency counters."""
    if getattr(app.state, "synergy_observability_installed", False):
        return
    app.state.synergy_observability_installed = True

    @app.middleware("http")
    async def synergy_observability(request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        started = time.perf_counter()
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            runtime.metrics.inc("http_exceptions_total", labels={"method": request.method, "path": request.url.path})
            raise
        finally:
            elapsed = time.perf_counter() - started
            # status is unavailable only when an exception escaped.
            if "status" in locals():
                labels={"method":request.method,"path":request.url.path,"status":str(status)}
                runtime.metrics.inc("http_requests_total", labels=labels)
                runtime.metrics.observe("http_request_duration_seconds", elapsed, labels=labels)
        response.headers["X-Request-ID"] = rid
        return response
