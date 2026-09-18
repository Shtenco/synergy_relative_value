# Enterprise architecture — Relative Value v2.0.0

```text
Client / Fund Network
        |
        v
OIDC/mTLS Gateway or HS256 service token
        |
        v
FastAPI Enterprise Boundary
  |         |            |
  |         |            +--> /enterprise/health + /metrics
  |         +--> RBAC + request-id correlation
  +--> pairs, synthetic-spread and carry research under explicit costs and hedge assumptions
        |
        +--> deterministic product core
        |
        +--> Venue adapters: Bybit V5 / CCXT / MetaTrader 5 (live gated)
        |
        +--> AuditEvent
               |--> PostgreSQL authoritative operational log
               +--> ClickHouse analytical mirror
```

## Boundary rules

- The product core remains separately testable and does not require database or venue connectivity for research/demo operation.
- Authentication/RBAC lives at the enterprise boundary. `admin` may perform all role-gated actions; other roles are explicit and tenant-scoped.
- `X-Request-ID` is propagated to responses and state-changing product calls are linked to the same identifier in the audit trail.
- Live venue execution is disabled by default. `SYNERGY_ALLOW_LIVE_EXECUTION=true` is necessary but is not sufficient by itself: customer credentials, scopes, canary limits and operational approval are still required.
- PostgreSQL is the authoritative control/audit store; ClickHouse is an optional high-volume analytical mirror.
- Retry and circuit-breaker logic is bounded. The system does not retry unknown financial side effects without a client/order idempotency identity.

## Adapters

- **Bybit V5:** deterministic HMAC signing, public ticker snapshot, live order endpoint behind explicit gate, client order id propagation.
- **CCXT:** lazy multi-CEX adapter for supported exchanges, rate-limit-aware client construction, dry-run without importing/initializing exchange clients.
- **MetaTrader 5:** lazy terminal initialization, tick snapshot, normalized market order, live disabled by default.

## Observability

The service exposes health and Prometheus text metrics and adds `X-Request-ID` to every HTTP response. Metrics include request counts, status/path labels, request duration summaries and audited product action counts. Audit data is structured evidence, not a substitute for application logs, broker statements or regulatory records.
