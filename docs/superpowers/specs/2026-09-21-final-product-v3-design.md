# Relative Value V3 Final Product Design

**Version:** 3.0.0  
**Branch:** `production/v3.0.0`  
**Status:** architecture specification for human review

## Goal
Convert Relative Value from a stateless pair-fit calculator into a persistent relative-value research platform with versioned pair definitions, fit artifacts, model freshness, refit policy and OOS evidence.

## Current gap
Today the caller supplies x/y arrays and receives alpha/beta/z-score/carry. No model identity, fit time, OOS state or refit lifecycle survives the request.

## Durable resources
- InstrumentPair
- PairUniverse
- PairModelVersion
- FitArtifact
- RefitPolicy
- SignalArtifact
- OOSValidationReference

## Core invariants
1. Every signal references one immutable model version.
2. A refit creates a new model version; old models remain queryable.
3. Model freshness is explicit.
4. Stale models cannot silently emit a current signal.
5. Fit success and OOS validation are separate states.
6. Dataset identity/hash and fitting window are stored.
7. Customer cost/carry/hedge conventions are versioned.

## V3 API
- `POST /enterprise/v3/pairs`
- `GET /enterprise/v3/pairs/{id}`
- `POST /enterprise/v3/pairs/{id}/fit`
- `GET /enterprise/v3/models/{id}`
- `POST /enterprise/v3/models/{id}/signal`
- `POST /enterprise/v3/models/{id}/validate`
- `GET /enterprise/v3/models?pair_id=...`

## Persistence
PostgreSQL:
- instrument_pairs
- pair_universes
- pair_model_versions
- fit_artifacts
- refit_policies
- signal_artifacts
- oos_validation_references
- idempotency_keys
- audit_events

## Model artifact
Stores fit window, dataset hash, alpha, beta, spread mean/std, method version, fitted_at, freshness deadline, code version and validation state.

## Numerical safety
Reject NaN/Inf; misaligned series; insufficient observations; zero/invalid volatility where unsupported; impossible correlation bounds; invalid timestamps.

## Acceptance gates
- model survives restart;
- stale model behavior is tested;
- refit creates new model ID/version;
- signal always cites model ID;
- cross-tenant isolation;
- idempotent fit creation;
- DB outage -> readiness 503;
- OOS reference can be attached without rewriting fit history;
- V2 tests remain green.
