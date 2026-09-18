# SYNERGY Relative Value

> **Pairs, synthetic-cross, carry and market-neutral research engine**

Version: `2.0.0`

**Enterprise v2.0.0** · FastAPI/OpenAPI · Docker/Compose · RBAC/JWT · PostgreSQL/ClickHouse audit

**Designed for:** FX desks, macro funds, prop firms and systematic relative-value teams  
**Primary endpoint:** `POST /enterprise/v1/relative-value/analyze`

> [!IMPORTANT]
> Research infrastructure only. Pair relationships, z-scores and carry do not guarantee market-neutrality or profit.

## Verification
**20 tests passed** · health smoke **80/80 200** · local p95 **59.8 ms** (~652 req/s). Health smoke only.

## Quick start
```bash
pip install -e '.[dev,enterprise]'
pytest -q
python -m synergy_relative_value.api
```

## CTO package
[Due diligence](docs/CTO_DUE_DILIGENCE.md) · [Architecture](docs/ARCHITECTURE_DIAGRAMS.md) · [API](docs/API_EXAMPLES.md) · [Security](SECURITY.md) · [Benchmarks](docs/BENCHMARKS_AND_ACCEPTANCE.md) · [SLA/SLO](docs/SLA_SLO.md) · [Deployment](docs/DEPLOYMENT_CHECKLIST.md) · [Pilot](docs/CUSTOMER_PILOT.md)
