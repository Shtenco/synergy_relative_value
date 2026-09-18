# Enterprise deployment

## Control plane

1. Copy `.env.enterprise.example` to `.env.enterprise`, then populate it from a secret manager or deployment secret source; never commit populated credentials.
2. Set `SYNERGY_ENV=prod` and a high-entropy `SYNERGY_AUTH_SECRET` or place the service behind the customer's OIDC/mTLS gateway.
3. Configure PostgreSQL as the authoritative audit sink. Add ClickHouse when analytical event throughput warrants it.
4. Keep `SYNERGY_ALLOW_LIVE_EXECUTION=false` until broker/CEX credentials, account scopes, kill-switch procedure, canary notional and incident response have been approved.
5. Run `docker compose -f deploy/docker-compose.enterprise.yml up --build` in a controlled environment.

## Production gates

- independent application/security review;
- customer-specific authorization matrix;
- encrypted secrets/KMS/HSM policy;
- venue sandbox/canary certification;
- time synchronization and clock monitoring;
- backup/restore test for PostgreSQL;
- ClickHouse retention review;
- load test on target hardware;
- live-operation runbook and rollback/kill-switch exercise.

The repository is an enterprise deployment candidate, not a claim that a customer's regulated production approval has already been completed.
