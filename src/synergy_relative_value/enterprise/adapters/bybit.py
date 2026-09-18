from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from urllib.parse import urlencode

from .base import MarketSnapshot, OrderRequest, OrderResult, TransportResponse, UrllibTransport
from ..resilience import CircuitBreaker, RetryPolicy


class BybitV5Adapter:
    venue = "bybit"

    def __init__(
        self,
        *,
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.bybit.com",
        category: str = "linear",
        recv_window: int = 5000,
        timeout_seconds: float = 5.0,
        transport=None,
        retry: RetryPolicy | None = None,
        breaker: CircuitBreaker | None = None,
        allow_live: bool = False,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.category = category
        self.recv_window = recv_window
        self.timeout_seconds = timeout_seconds
        self.transport = transport or UrllibTransport()
        self.retry = retry or RetryPolicy()
        self.breaker = breaker or CircuitBreaker()
        self.allow_live = allow_live

    def signed_headers(self, body: str, *, timestamp_ms: int | None = None) -> dict[str, str]:
        ts = int(time.time() * 1000) if timestamp_ms is None else int(timestamp_ms)
        payload = f"{ts}{self.api_key}{self.recv_window}{body}"
        signature = hmac.new(self.api_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": str(ts),
            "X-BAPI-RECV-WINDOW": str(self.recv_window),
            "X-BAPI-SIGN": signature,
            "Content-Type": "application/json",
        }

    def _call(self, method: str, url: str, *, headers=None, body=None) -> TransportResponse:
        def op():
            response = self.transport.request(method, url, headers=headers, body=body, timeout=self.timeout_seconds)
            if response.status_code >= 500:
                raise ConnectionError(f"venue server error {response.status_code}")
            return response
        return self.breaker.call(lambda: self.retry.call(op))

    def snapshot(self, symbol: str) -> MarketSnapshot:
        query = urlencode({"category": self.category, "symbol": symbol})
        response = self._call("GET", f"{self.base_url}/v5/market/tickers?{query}")
        if response.status_code >= 400 or int(response.json_data.get("retCode", 0)) != 0:
            raise RuntimeError(f"Bybit market data error: {response.json_data}")
        rows = response.json_data.get("result", {}).get("list", [])
        if not rows:
            raise RuntimeError("Bybit returned no ticker rows")
        row = rows[0]
        f = lambda x: float(x) if x not in (None, "") else None
        return MarketSnapshot(self.venue, symbol, f(row.get("bid1Price")), f(row.get("ask1Price")), f(row.get("lastPrice")), int(response.json_data.get("time", 0)) or None)

    def execute(self, order: OrderRequest) -> OrderResult:
        if order.quantity <= 0:
            raise ValueError("quantity must be positive")
        client_id = order.client_order_id or f"synergy-{uuid.uuid4().hex[:24]}"
        if not self.allow_live:
            return OrderResult(self.venue, "DRY_RUN", order.quantity, client_order_id=client_id, raw={"live": False})
        payload = {
            "category": self.category,
            "symbol": order.symbol,
            "side": order.side,
            "orderType": order.order_type,
            "qty": format(order.quantity, ".15g"),
            "orderLinkId": client_id,
        }
        if order.price is not None:
            payload["price"] = format(order.price, ".15g")
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        response = self._call("POST", f"{self.base_url}/v5/order/create", headers=self.signed_headers(body), body=body)
        if response.status_code >= 400 or int(response.json_data.get("retCode", -1)) != 0:
            raise RuntimeError(f"Bybit order rejected: {response.json_data}")
        result = response.json_data.get("result", {})
        return OrderResult(
            venue=self.venue,
            status="ACCEPTED",
            requested_quantity=order.quantity,
            external_id=result.get("orderId"),
            client_order_id=result.get("orderLinkId") or client_id,
            raw=dict(response.json_data),
        )
