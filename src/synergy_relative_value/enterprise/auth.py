from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Iterable

from .models import Principal, Role


class AuthError(ValueError):
    pass


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _json(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_token(
    secret: str,
    *,
    subject: str,
    roles: Iterable[Role | str],
    tenant_id: str = "default",
    ttl_seconds: int = 900,
    now: int | float | None = None,
    issuer: str = "synergy",
    audience: str = "synergy-enterprise",
) -> str:
    if not secret or len(secret) < 16:
        raise AuthError("auth secret must contain at least 16 characters")
    if ttl_seconds <= 0:
        raise AuthError("ttl_seconds must be positive")
    issued = int(time.time() if now is None else now)
    role_values = sorted({Role(r).value for r in roles})
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "roles": role_values,
        "tenant_id": tenant_id,
        "iat": issued,
        "exp": issued + int(ttl_seconds),
        "iss": issuer,
        "aud": audience,
        "jti": str(uuid.uuid4()),
    }
    signing_input = f"{_b64e(_json(header))}.{_b64e(_json(payload))}"
    sig = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64e(sig)}"


def verify_token(
    token: str,
    secret: str,
    *,
    now: int | float | None = None,
    issuer: str = "synergy",
    audience: str = "synergy-enterprise",
) -> Principal:
    try:
        h, p, s = token.split(".")
        header = json.loads(_b64d(h))
        payload = json.loads(_b64d(p))
    except Exception as exc:
        raise AuthError("malformed bearer token") from exc
    if header.get("alg") != "HS256" or header.get("typ") != "JWT":
        raise AuthError("unsupported token header")
    expected = hmac.new(secret.encode("utf-8"), f"{h}.{p}".encode("ascii"), hashlib.sha256).digest()
    try:
        actual = _b64d(s)
    except Exception as exc:
        raise AuthError("malformed signature") from exc
    if not hmac.compare_digest(expected, actual):
        raise AuthError("invalid signature")
    current = int(time.time() if now is None else now)
    if int(payload.get("exp", 0)) < current:
        raise AuthError("token expired")
    if int(payload.get("iat", current)) > current + 30:
        raise AuthError("token issued in the future")
    if payload.get("iss") != issuer or payload.get("aud") != audience:
        raise AuthError("issuer or audience mismatch")
    subject = str(payload.get("sub") or "").strip()
    if not subject:
        raise AuthError("missing subject")
    try:
        roles = frozenset(Role(r) for r in payload.get("roles", []))
    except ValueError as exc:
        raise AuthError("unknown role") from exc
    return Principal(
        subject=subject,
        roles=roles,
        tenant_id=str(payload.get("tenant_id") or "default"),
        token_id=str(payload.get("jti")) if payload.get("jti") else None,
    )


def require_role(principal: Principal, allowed: set[Role] | frozenset[Role]) -> None:
    if Role.ADMIN in principal.roles:
        return
    if not principal.roles.intersection(allowed):
        raise PermissionError("role not permitted")
