from synergy_relative_value.synergy_contracts import CONTRACT_ID, relative_value_signal_payload

def test_relative_value_signal_is_advisory():
    x=[1+i*.01 for i in range(20)]
    y=[2+1.5*v for v in x]
    p=relative_value_signal_payload(
        observation_id="rv1",symbol_x="EURUSD",symbol_y="GBPUSD",
        x_history=x,y_history=y,x_now=x[-1],y_now=y[-1]+.1
    )
    assert CONTRACT_ID=="synergy.trading.relative-value-signal/v1"
    assert p["authorization"] is False
    assert p["requires_domain_validation"] is True
