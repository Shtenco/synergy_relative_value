# RBAC model

Roles are tenant-scoped JWT claims: `viewer`, `researcher`, `trader`, `risk`, `operator`, `admin`.

- `viewer`: health/identity/read-only product views.
- `researcher`: validation, analytics and model research actions.
- `trader`: execution planning, quoting and approved trade-intent workflows.
- `risk`: risk decisions, vetoes and governance checks.
- `operator`: venue/runtime operations and controlled execution plumbing.
- `admin`: audit access and all role-gated actions.

The built-in HS256 verifier exists for self-contained deployments and demos. Production financial deployments should terminate authentication at an enterprise OIDC/mTLS gateway or extend the verifier to asymmetric JWT/JWKS validation with managed key rotation. Do not share one HMAC secret across unrelated customers.
