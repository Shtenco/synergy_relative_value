import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_customer_demo_is_synthetic_structured_and_secret_free():
    path=ROOT/'demo/customer_demo.jsonl'
    rows=[json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    assert len(rows)>=25
    assert all({'timestamp','tenant_id','request_id'} <= set(r) for r in rows)
    text=path.read_text().lower()
    for forbidden in ['private_key','api_secret','password=', 'begin private key']:
        assert forbidden not in text
    assert rows==[json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def test_load_harnesses_exist():
    assert (ROOT/'loadtests/benchmark.py').exists()
    assert (ROOT/'loadtests/k6_smoke.js').exists()
