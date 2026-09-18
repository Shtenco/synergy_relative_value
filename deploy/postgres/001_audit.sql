CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL,
    tenant_id TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    request_id TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_ts
    ON audit_events (tenant_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_events_request
    ON audit_events (tenant_id, request_id);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    tenant_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    operation TEXT NOT NULL,
    response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ,
    PRIMARY KEY (tenant_id, idempotency_key, operation)
);
