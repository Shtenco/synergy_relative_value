from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
import json
import urllib.request


@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    side: str
    quantity: float
    order_type: str = "Market"
    price: float | None = None
    client_order_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrderResult:
    venue: str
    status: str
    requested_quantity: float
    filled_quantity: float = 0.0
    avg_price: float | None = None
    fee: float | None = None
    external_id: str | None = None
    client_order_id: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MarketSnapshot:
    venue: str
    symbol: str
    bid: float | None
    ask: float | None
    last: float | None
    timestamp_ms: int | None = None


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    json_data: Mapping[str, Any]
    headers: Mapping[str, str] = field(default_factory=dict)


class HttpTransport(Protocol):
    def request(self, method: str, url: str, *, headers: Mapping[str, str] | None = None, body: str | None = None, timeout: float = 5.0) -> TransportResponse: ...


class UrllibTransport:
    def request(self, method: str, url: str, *, headers=None, body=None, timeout: float = 5.0) -> TransportResponse:
        req = urllib.request.Request(url=url, data=body.encode("utf-8") if body is not None else None, headers=dict(headers or {}), method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw) if raw else {}
                return TransportResponse(response.status, data, dict(response.headers.items()))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw) if raw else {"error": str(exc)}
            except json.JSONDecodeError:
                data = {"error": raw or str(exc)}
            return TransportResponse(exc.code, data, dict(exc.headers.items()) if exc.headers else {})


class VenueAdapter(Protocol):
    venue: str
    def snapshot(self, symbol: str) -> MarketSnapshot: ...
    def execute(self, order: OrderRequest) -> OrderResult: ...
