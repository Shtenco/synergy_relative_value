from fastapi import FastAPI
from fastapi.testclient import TestClient
from synergy_relative_value.enterprise.models import Role, AuditEvent
from synergy_relative_value.enterprise.auth import sign_token
from synergy_relative_value.enterprise.audit import InMemoryAuditStore
from synergy_relative_value.enterprise.metrics import MetricsRegistry
from synergy_relative_value.enterprise.service import EnterpriseRuntime, build_enterprise_router, install_observability

SECRET="service-test-secret-with-enough-entropy"

def bearer(role):
    return {"Authorization":"Bearer "+sign_token(SECRET,subject="tester",roles=[role],ttl_seconds=3600)}

def test_metrics_render_prometheus():
    m=MetricsRegistry(namespace="synergy_test")
    m.inc("requests_total", labels={"route":"health"})
    m.observe("latency_seconds",0.12,labels={"route":"health"})
    text=m.render_prometheus()
    assert 'synergy_test_requests_total{route="health"} 1.0' in text
    assert 'synergy_test_latency_seconds_count{route="health"} 1' in text

def test_health_whoami_and_admin_audit_endpoint():
    store=InMemoryAuditStore()
    store.append(AuditEvent.create(tenant_id="default",actor="system",action="seed",request_id="seed-1",payload={}))
    runtime=EnterpriseRuntime(service_name="svc",auth_secret=SECRET,audit_store=store)
    app=FastAPI();install_observability(app,runtime);app.include_router(build_enterprise_router(runtime))
    c=TestClient(app)
    health=c.get('/enterprise/health',headers={"X-Request-ID":"trace-1"})
    assert health.status_code==200
    assert health.headers["X-Request-ID"]=="trace-1"
    who=c.get('/enterprise/whoami',headers=bearer(Role.VIEWER))
    assert who.status_code==200 and who.json()['subject']=='tester'
    assert c.get('/enterprise/audit',headers=bearer(Role.RESEARCHER)).status_code==403
    audit=c.get('/enterprise/audit',headers=bearer(Role.ADMIN))
    assert audit.status_code==200 and audit.json()[0]['action']=='seed'
