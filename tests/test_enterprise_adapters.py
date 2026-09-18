import pytest
from synergy_relative_value.enterprise.adapters.base import OrderRequest, TransportResponse
from synergy_relative_value.enterprise.adapters.bybit import BybitV5Adapter
from synergy_relative_value.enterprise.adapters.mt5 import MT5Adapter
from synergy_relative_value.enterprise.adapters.ccxt import CCXTAdapter
from synergy_relative_value.enterprise.resilience import CircuitBreaker, CircuitOpenError, RetryPolicy

class FakeTransport:
    def __init__(self, responses=None):
        self.responses=list(responses or [])
        self.calls=[]
    def request(self, method, url, *, headers=None, body=None, timeout=5.0):
        self.calls.append((method,url,headers or {},body,timeout))
        if not self.responses:
            return TransportResponse(200,{"retCode":0,"result":{"orderId":"oid-1"}})
        item=self.responses.pop(0)
        if isinstance(item,Exception): raise item
        return item

def test_bybit_dry_run_never_touches_network():
    tx=FakeTransport()
    adapter=BybitV5Adapter(api_key="k",api_secret="s",transport=tx,allow_live=False)
    result=adapter.execute(OrderRequest(symbol="BTCUSDT",side="Buy",quantity=0.01,client_order_id="cid-1"))
    assert result.status=="DRY_RUN"
    assert result.client_order_id=="cid-1"
    assert tx.calls==[]

def test_bybit_signature_is_deterministic():
    adapter=BybitV5Adapter(api_key="key",api_secret="secret",transport=FakeTransport(),allow_live=True)
    body='{"category":"linear","orderLinkId":"abc","orderType":"Market","qty":"1","side":"Buy","symbol":"BTCUSDT"}'
    headers=adapter.signed_headers(body, timestamp_ms=1700000000000)
    assert headers["X-BAPI-API-KEY"]=="key"
    assert headers["X-BAPI-TIMESTAMP"]=="1700000000000"
    assert len(headers["X-BAPI-SIGN"])==64
    assert headers["X-BAPI-SIGN"]==adapter.signed_headers(body, timestamp_ms=1700000000000)["X-BAPI-SIGN"]

def test_retry_and_circuit_breaker():
    attempts={"n":0}
    def flaky():
        attempts["n"]+=1
        if attempts["n"]<3: raise TimeoutError("temporary")
        return "ok"
    policy=RetryPolicy(max_attempts=3, base_delay_seconds=0)
    assert policy.call(flaky)=="ok"
    cb=CircuitBreaker(failure_threshold=2, recovery_seconds=60)
    for _ in range(2):
        with pytest.raises(RuntimeError): cb.call(lambda: (_ for _ in ()).throw(RuntimeError("boom")), now=0)
    with pytest.raises(CircuitOpenError): cb.call(lambda:"never", now=1)

def test_mt5_adapter_is_live_disabled_by_default():
    adapter=MT5Adapter(allow_live=False)
    result=adapter.execute(OrderRequest(symbol="EURUSD",side="Buy",quantity=0.1,client_order_id="mt5-demo"))
    assert result.status=="DRY_RUN"


def test_ccxt_adapter_dry_run_is_dependency_free():
    adapter=CCXTAdapter(exchange_id="binance",allow_live=False)
    result=adapter.execute(OrderRequest(symbol="BTC/USDT",side="buy",quantity=0.01,client_order_id="ccxt-demo"))
    assert result.status=="DRY_RUN"
    assert result.venue=="ccxt:binance"
