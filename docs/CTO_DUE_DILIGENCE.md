# CTO due diligence — SYNERGY Relative Value

Use case: Pairs, synthetic-cross, carry and market-neutral research engine. Buyer: FX desks, macro funds, prop firms and systematic relative-value teams. Endpoint `/enterprise/v1/relative-value/analyze`, roles **researcher, trader**.

Implemented: pair fitting, z-score/carry analysis, tenant RBAC, request-ID audit, PostgreSQL/ClickHouse, metrics and deployment assets. Evidence: **20 tests passed**, health smoke 80/80 200, local p95 **59.8 ms**.

Boundary: research engine only; relationship persistence, costs, capacity and market-neutrality require customer OOS/paper validation.