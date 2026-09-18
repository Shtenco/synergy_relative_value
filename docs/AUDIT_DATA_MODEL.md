# Audit data model

Every enterprise state-changing action emits an `AuditEvent` containing an immutable event id, UTC timestamp, tenant, actor, action, request id and JSON payload.

PostgreSQL is the authoritative operational audit store. ClickHouse is an optional analytical mirror for high-volume review, dashboards and incident analysis. `CompositeAuditStore` defaults to fail-closed behavior so a configured audit sink failure is visible instead of silently losing evidence.

Recommended retention is jurisdiction/customer-policy dependent. The reference ClickHouse schema uses a 730-day TTL only as an example deployment default; change it to the customer's legal and record-retention requirements.
