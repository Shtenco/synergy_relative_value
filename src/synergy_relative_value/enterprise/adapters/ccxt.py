from __future__ import annotations

import importlib
import uuid

from .base import MarketSnapshot, OrderRequest, OrderResult


class CCXTAdapter:
    """Lazy multi-CEX adapter. The ccxt dependency is only required for market/live calls."""

    def __init__(
        self,
        *,
        exchange_id: str,
        api_key: str = "",
        api_secret: str = "",
        password: str | None = None,
        allow_live: bool = False,
        exchange=None,
        options: dict | None = None,
    ) -> None:
        self.exchange_id = exchange_id
        self.venue = f"ccxt:{exchange_id}"
        self.api_key = api_key
        self.api_secret = api_secret
        self.password = password
        self.allow_live = allow_live
        self.options = dict(options or {})
        self._exchange = exchange

    def _client(self):
        if self._exchange is not None:
            return self._exchange
        try:
            ccxt = importlib.import_module("ccxt")
        except ImportError as exc:
            raise RuntimeError("install ccxt to use live/public multi-CEX connectivity") from exc
        cls = getattr(ccxt, self.exchange_id, None)
        if cls is None:
            raise ValueError(f"unsupported ccxt exchange: {self.exchange_id}")
        config = {"enableRateLimit": True, "options": self.options}
        if self.api_key:
            config["apiKey"] = self.api_key
        if self.api_secret:
            config["secret"] = self.api_secret
        if self.password:
            config["password"] = self.password
        self._exchange = cls(config)
        return self._exchange

    def snapshot(self, symbol: str) -> MarketSnapshot:
        ticker = self._client().fetch_ticker(symbol)
        f = lambda x: float(x) if x not in (None, "") else None
        return MarketSnapshot(
            self.venue,
            symbol,
            f(ticker.get("bid")),
            f(ticker.get("ask")),
            f(ticker.get("last")),
            int(ticker.get("timestamp")) if ticker.get("timestamp") else None,
        )

    def execute(self, order: OrderRequest) -> OrderResult:
        if order.quantity <= 0:
            raise ValueError("quantity must be positive")
        client_id = order.client_order_id or f"synergy-{uuid.uuid4().hex[:24]}"
        if not self.allow_live:
            return OrderResult(self.venue, "DRY_RUN", order.quantity, client_order_id=client_id, raw={"live": False})
        if not self.api_key or not self.api_secret:
            raise RuntimeError("live CCXT execution requires API credentials")
        params = dict(order.metadata)
        params.setdefault("clientOrderId", client_id)
        result = self._client().create_order(
            order.symbol,
            order.order_type.lower(),
            order.side.lower(),
            float(order.quantity),
            float(order.price) if order.price is not None else None,
            params,
        )
        fee = result.get("fee") or {}
        filled = float(result.get("filled") or 0.0)
        avg = result.get("average") or result.get("price")
        status = str(result.get("status") or "accepted").upper()
        return OrderResult(
            venue=self.venue,
            status=status,
            requested_quantity=order.quantity,
            filled_quantity=filled,
            avg_price=float(avg) if avg not in (None, "") else None,
            fee=float(fee.get("cost")) if isinstance(fee, dict) and fee.get("cost") not in (None, "") else None,
            external_id=str(result.get("id")) if result.get("id") else None,
            client_order_id=str(result.get("clientOrderId") or client_id),
            raw=dict(result),
        )
