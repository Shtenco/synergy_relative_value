# Deployment checklist — SYNERGY Relative Value

- [ ] Pin revision/image and rerun tests.
- [ ] Customer TLS + OIDC/mTLS/JWKS and KMS secrets.
- [ ] Configure audit DB and backup/restore.
- [ ] Freeze instrument mapping, sampling, carry/cost/hedge conventions.
- [ ] Exercise `/enterprise/v1/relative-value/analyze` on representative customer series.
- [ ] Prove roles **researcher, trader** and viewer denial.
- [ ] Run load/failure drills and keep execution separately gated.