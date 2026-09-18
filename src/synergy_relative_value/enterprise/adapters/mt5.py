from __future__ import annotations

import importlib
import time
import uuid

from .base import MarketSnapshot, OrderRequest, OrderResult


class MT5Adapter:
    venue = "mt5"

    def __init__(self, *, terminal_path: str | None = None, allow_live: bool = False, module=None) -> None:
        self.terminal_path = terminal_path
        self.allow_live = allow_live
        self._module = module
        self._initialized = False

    def _mt5(self):
        if self._module is None:
            try:
                self._module = importlib.import_module("MetaTrader5")
            except ImportError as exc:
                raise RuntimeError("install MetaTrader5 package on a supported host to use MT5Adapter") from exc
        if not self._initialized:
            kwargs = {"path": self.terminal_path} if self.terminal_path else {}
            if not self._module.initialize(**kwargs):
                raise RuntimeError(f"MT5 initialize failed: {self._module.last_error()}")
            self._initialized = True
        return self._module

    def snapshot(self, symbol: str) -> MarketSnapshot:
        mt5 = self._mt5()
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"MT5 has no tick for {symbol}: {mt5.last_error()}")
        return MarketSnapshot(self.venue, symbol, float(tick.bid), float(tick.ask), float(tick.last) if getattr(tick, "last", 0) else None, int(getattr(tick, "time_msc", time.time()*1000)))

    def execute(self, order: OrderRequest) -> OrderResult:
        if order.quantity <= 0:
            raise ValueError("quantity must be positive")
        client_id = order.client_order_id or f"synergy-{uuid.uuid4().hex[:20]}"
        if not self.allow_live:
            return OrderResult(self.venue, "DRY_RUN", order.quantity, client_order_id=client_id, raw={"live": False})
        mt5 = self._mt5()
        tick = mt5.symbol_info_tick(order.symbol)
        if tick is None:
            raise RuntimeError(f"MT5 has no tick for {order.symbol}")
        buy = order.side.lower() in {"buy", "long"}
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": order.symbol,
            "volume": float(order.quantity),
            "type": mt5.ORDER_TYPE_BUY if buy else mt5.ORDER_TYPE_SELL,
            "price": float(order.price if order.price is not None else (tick.ask if buy else tick.bid)),
            "deviation": int(order.metadata.get("deviation", 20)),
            "magic": int(order.metadata.get("magic", 260919)),
            "comment": client_id[:31],
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": int(order.metadata.get("type_filling", mt5.ORDER_FILLING_IOC)),
        }
        result = mt5.order_send(request)
        if result is None:
            raise RuntimeError(f"MT5 order_send returned None: {mt5.last_error()}")
        ok = int(result.retcode) in {int(getattr(mt5, "TRADE_RETCODE_DONE", -999)), int(getattr(mt5, "TRADE_RETCODE_PLACED", -998))}
        return OrderResult(
            venue=self.venue,
            status="FILLED" if ok else "REJECTED",
            requested_quantity=order.quantity,
            filled_quantity=float(getattr(result, "volume", 0.0) or 0.0),
            avg_price=float(getattr(result, "price", 0.0) or 0.0) or None,
            external_id=str(getattr(result, "order", "") or getattr(result, "deal", "") or "") or None,
            client_order_id=client_id,
            raw={"retcode": int(result.retcode), "comment": str(getattr(result, "comment", ""))},
        )
