import pytest
from synergy_relative_value.enterprise.models import Role, AuditEvent
from synergy_relative_value.enterprise.auth import sign_token, verify_token, require_role, AuthError
from synergy_relative_value.enterprise.audit import InMemoryAuditStore, CompositeAuditStore

SECRET="unit-test-secret-with-enough-entropy"

def test_signed_token_roundtrip_and_rbac():
    token=sign_token(SECRET, subject="alice", roles=[Role.RESEARCHER], ttl_seconds=60, now=1_700_000_000)
    principal=verify_token(token, SECRET, now=1_700_000_010)
    assert principal.subject=="alice"
    assert Role.RESEARCHER in principal.roles
    require_role(principal, {Role.RESEARCHER, Role.ADMIN})
    with pytest.raises(PermissionError):
        require_role(principal, {Role.ADMIN})

def test_expired_token_is_rejected():
    token=sign_token(SECRET, subject="alice", roles=[Role.VIEWER], ttl_seconds=5, now=100)
    with pytest.raises(AuthError):
        verify_token(token, SECRET, now=106)

def test_audit_event_and_composite_store_fanout():
    a,b=InMemoryAuditStore(),InMemoryAuditStore()
    store=CompositeAuditStore([a,b])
    event=AuditEvent.create(tenant_id="fund-1", actor="alice", action="test.action", request_id="req-1", payload={"x":1})
    store.append(event)
    assert a.query("fund-1", limit=10)[0].event_id==event.event_id
    assert b.query("fund-1", limit=10)[0].request_id=="req-1"
    assert event.payload=={"x":1}
