CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID,
    ts DateTime64(6, 'UTC'),
    tenant_id LowCardinality(String),
    actor String,
    action LowCardinality(String),
    request_id String,
    payload String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, ts, event_id)
TTL ts + INTERVAL 730 DAY;
