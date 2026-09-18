# Product status

## Commercial status
This repository is packaged as an **enterprise-deployment candidate and paid-pilot product**. Version `2.0.0` adds a production-oriented control plane around the deterministic product core: role-based authentication, auditable request identity, database-backed audit sinks, live-gated venue adapters, observability, deployment stack and load/customer-demo tooling.

## Ready to sell means
- standalone installable product with REST/OpenAPI boundary;
- deterministic core and enterprise acceptance tests;
- tenant-scoped roles and authenticated privileged endpoints;
- PostgreSQL/ClickHouse audit path;
- Bybit V5, CCXT multi-CEX and MetaTrader 5 adapter contracts with live execution disabled by default;
- Docker Compose reference deployment and synthetic demo dataset;
- documented customer acceptance gates and commercial claim boundary.

## Production status boundary
`2.0.0` is **not a statement that any particular fund, broker or regulator has approved production use**. Production activation requires customer-specific security review, venue/account certification, limits and risk sign-off, legal/compliance approval, measured SLO/load results, incident/rollback drills and a controlled canary.

No repository promises trading profit. Alpha, market impact, execution quality, capacity and portfolio outcomes must be validated on the customer's own data, venues and constraints.
