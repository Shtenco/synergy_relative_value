# Security and trading-control boundary

1. No API keys or broker secrets belong in source control.
2. Live trading is disabled in the supplied reference configuration.
3. Production adapters must use a secret manager/HSM/MPC where appropriate.
4. All decisions and executions should carry immutable correlation IDs and audit records.
5. Risk veto must sit outside mutable strategy/LLM logic.
6. Customer-specific legal, licensing, KYC/AML, market-abuse and venue rules remain deployment requirements.
7. Any benchmark must include realistic fees, spread, slippage, latency and capacity constraints.

## Enterprise v2 security controls
- JWT/RBAC is enforced at enterprise endpoints; production should prefer customer OIDC/mTLS or managed asymmetric JWT/JWKS.
- Live venue execution remains opt-in and must use least-privilege API keys with withdrawals disabled where the venue permits.
- Secrets belong in a secret manager/KMS, never `.env` committed to Git.
- Audit-sink failure is visible/fail-closed when a composite audit backend is configured.
- Request IDs are correlation identifiers, not authentication or idempotency secrets.
