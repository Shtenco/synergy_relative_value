# Enterprise load testing

Two harnesses are included:

- `python loadtests/benchmark.py --requests 1000 --concurrency 32` for dependency-free HTTP pressure testing.
- `k6 run loadtests/k6_smoke.js` for an external black-box smoke/load profile.

The k6 thresholds are **acceptance targets, not measured performance claims**: error rate below 0.1% and HTTP p95 below 250 ms on the chosen reference environment. Record hardware, container limits, dataset size, endpoint, authentication mode and database backends with every benchmark result.

Never benchmark a live brokerage/CEX execution endpoint with real credentials or capital. Use dry-run/paper adapters unless a controlled canary environment is explicitly approved.
